import csv
import datetime
import json
import logging
import os

import ijson
import psycopg2
from ocdskit.combine import merge
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import NotConfigured, UsageError

from kingfisher_scrapy import util

logger = logging.getLogger(__name__)


class IncrementalDataStore(ScrapyCommand):

    connection = None
    cursor = None

    def syntax(self):
        return '[options] <spider_name> <db_schema_name> <crawl_time>'

    def short_desc(self):
        return 'Download OCDS data and store it in a PostgresSQL database, incrementally'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option('--compile', action='store_true',
                          help='Merge individual releases into compiled releases')

    def from_date_formatted(self, date, date_format):
        if date_format == 'datetime':
            return date[:19]
        if date_format == 'date':
            return date[:10]
        if date_format == 'year-month':
            return date[:7]
        return date[:4]

    def database_setup(self, table_and_schema_name):
        """
        Creates the database connection, sets the search path and creates the required table if it doesn't exists yet.
        """
        self.connection = psycopg2.connect(os.getenv('KINGFISHER_COLLECT_DATABASE_URL'))
        self.cursor = self.connection.cursor()
        self.cursor.execute(f'SET search_path = {table_and_schema_name}')
        self.create_table(table_and_schema_name)

    def create_table(self, table_name):
        """
        Creates a table with a jsonb "data" column and creates and index on the data->>'date' field
        """
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (data jsonb)')

    def get_data_from_directory(self, data_directory, prefix=''):
        """
        Yields items from jsons files in the given directory
        :param data_directory directory from where read the json files
        :param prefix the path from which read the data from the json file. By default the complete json file
        """
        for dir_entry in os.scandir(data_directory):
            if dir_entry.name.endswith('.json'):
                with open(dir_entry.path) as f:
                    yield from ijson.items(f, prefix)

    def json_to_csv(self, data, data_directory):
        """
        Receives an iterable of json dicts and save them into a data.csv file in the given directory
        :param data an iterable of json dict
        :param data_directory directory to where create the csv file
        """
        file_name = os.path.join(data_directory, 'data.csv')
        with open(file_name, 'w') as f:
            writer = csv.writer(f)
            for item in data:
                data = json.dumps(item, default=util.default)
                writer.writerow([data])
        return file_name

    def run(self, args, opts):
        if not self.settings['FILES_STORE'] or not os.getenv('KINGFISHER_COLLECT_DATABASE_URL'):
            raise NotConfigured('FILES_STORE and/or KINGFISHER_COLLECT_DATABASE_URL is not set.')

        spiders = self.crawler_process.spider_loader.list()
        if len(args) < 3:
            raise UsageError('A valid spider, database schema nme, and crawl time must be given.')

        spider_name = args[0]
        db_schema_name = table_name = args[1]
        try:
            crawl_time = datetime.datetime.strptime(args[2], '%Y-%m-%dT%H:%M:%S')
            folder_name = crawl_time.strftime('%Y%m%d_%H%M%S')
        except ValueError as e:
            raise UsageError(f'argument `crawl_time`: invalid date value: {e}')

        if not spider_name or spider_name not in spiders:
            raise UsageError('A valid spider must be given.')

        spidercls = self.crawler_process.spider_loader.load(spider_name)

        if 'record' in spidercls.data_type and opts.compile:
            raise UsageError('The --compile option can only be used with spiders that return releases.')

        # Disable the Kingfisher Process extension.
        self.settings['EXTENSIONS']['kingfisher_scrapy.extensions.KingfisherProcessAPI'] = None

        self.database_setup(db_schema_name)

        # Get the most recent date in the spider's data table.
        self.cursor.execute(f"SELECT max(data->>'date') FROM {table_name}")
        last_date = self.cursor.fetchone()[0]

        logger.info(f'Running: scrapy crawl {spider_name} -a from_date={last_date} -a crawl_time={crawl_time}')

        kwargs = {'crawl_time': crawl_time}

        # If there is data already in the database we only download data after the last release date
        if last_date:
            kwargs['from_date'] = self.from_date_formatted(last_date, spidercls.date_format)
        self.crawler_process.crawl(spidercls, **kwargs)
        self.crawler_process.start()

        data_directory = os.path.join(self.settings['FILES_STORE'], f'{spider_name}', folder_name)

        logger.info('Starting the compile/file reading process')
        if opts.compile:
            list_type = ''
        # if we don't need to compile the releases, we insert them directly in the database
        else:
            if 'release' in spidercls.data_type:
                list_type = 'releases.item'
            else:
                list_type = 'records.item.compiledRelease'
        data = self.get_data_from_directory(data_directory, list_type)

        if opts.compile:
            data = merge(data)

        csv_file_name = self.json_to_csv(data, data_directory)
        # Replace the spider's data table.
        self.cursor.execute(f'DROP TABLE {table_name} CASCADE ')
        self.create_table(spider_name)

        logger.info('Dumping the data into the data base')
        with open(csv_file_name) as f:
            self.cursor.copy_expert(f"COPY {table_name}(data) FROM STDIN WITH CSV", f)
        os.remove(csv_file_name)
        self.cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name} ON {table_name}(cast(data->>'date' as text))")
        self.connection.commit()
