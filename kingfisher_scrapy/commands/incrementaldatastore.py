import csv
import datetime
import json
import logging
import os

import ijson
import psycopg2
from ocdskit.combine import merge
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError, NotConfigured

from kingfisher_scrapy import util

# these can be a command line argument as well
CRAWL_TIME = '2021-04-22T00:00:00'
FOLDER_NAME = datetime.datetime.strptime(CRAWL_TIME, '%Y-%m-%dT%H:%M:%S').strftime('%Y%m%d_%H%M%S')

logger = logging.getLogger(__name__)


class IncrementalDataStore(ScrapyCommand):
    def syntax(self):
        return '[options] --spider spider_name --db_schema schema'

    def short_desc(self):
        return 'Store compile releases from the given spider in a PostgresSQL database, incrementally'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option('--spider', type=str, help='The spider to run')
        parser.add_option('--db_schema', type=str, help='The existing database schema to use')
        parser.add_option('--compile', action='store_true', help='Compile the releases before saving them to the '
                                                                 'database')

    def from_date_formatted(self, last_date, date_format):
        """
        Returns the date formatted as the specified spider date format
        """
        if date_format == 'datetime':
            return last_date[0:19]
        elif date_format == 'date':
            return last_date[0:10]
        elif date_format == 'year-month':
            return last_date[0:7]
        else:
            return last_date[0:6]

    def database_setup(self, spider_name, schema_name):
        """
        Creates the database connection, set the search path and create the required table if it doesn't exists yet.
        """
        connection = psycopg2.connect(os.getenv('KINGFISHER_COLLECT_DATABASE_URL'))
        cursor = connection.cursor()
        cursor.execute(f'SET search_path = {schema_name}')
        self.create_table(cursor, spider_name)
        return connection, cursor

    def create_table(self, cursor, spider_name):
        """
        Creates a table with a jsonb "data" column and creates and index on the data->>'date' field
        """
        cursor.execute(f'CREATE TABLE IF NOT EXISTS {spider_name} (data jsonb);')

    def run_spider(self, last_date, spidercls):
        kwargs = {'crawl_time': CRAWL_TIME}

        # If there is data already in the database we only download data after the last release date
        if last_date:
            kwargs['from_date'] = self.from_date_formatted(last_date, spidercls.date_format)
        self.crawler_process.crawl(spidercls, **kwargs)
        self.crawler_process.start()

    def get_data_from_directory(self, data_directory, json_data_path=''):
        """
        Yields items from jsons files in the given directory
        :param data_directory directory from where read the json files
        :param json_data_path the path from which read the data from the json file. By default the complete json file
        """
        for dir_entry in os.scandir(data_directory):
            if dir_entry.name.endswith('.json'):
                with open(dir_entry.path) as f:
                    yield from ijson.items(f, json_data_path)

    def json_to_csv(self, data, data_directory):
        """
        Receives an iterable of json dicts and save them into a data.csv file in the given directory
        :param data an iterable of json dict
        :param data_directory directory to where create the csv file
        """
        file_name = os.path.join(data_directory, 'data.csv')
        with open(file_name, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            for item in data:
                data = json.dumps(item, default=util.default)
                csv_writer.writerow([data])
        return file_name

    def run(self, args, opts):

        if not self.settings['FILES_STORE'] or not os.getenv('KINGFISHER_COLLECT_DATABASE_URL'):
            raise NotConfigured('You must set a FILES_STORE and KINGFISHER_COLLECT_DATABASE_URL')

        spiders = self.crawler_process.spider_loader.list()
        spider_name = opts.spider

        if not spider_name or opts.spider not in spiders:
            raise UsageError('A valid spider must be given.')

        if not opts.db_schema:
            raise UsageError('A database schema name must be given.')

        spidercls = self.crawler_process.spider_loader.load(spider_name)

        if 'record' in spidercls.data_type and opts.compile:
            raise UsageError('The compile option can only be used with spiders that returns releases.')

        # we disable kingfisher process extension
        self.settings['EXTENSIONS']['kingfisher_scrapy.extensions.KingfisherProcessAPI'] = None

        connection, cursor = self.database_setup(spider_name, opts.db_schema)

        # gets the last data->>'date' that exists in the country table
        cursor.execute(f"SELECT max(data->>'date') FROM {spider_name};")
        last_date = cursor.fetchone()[0]

        logger.info(f'Last release date found {last_date}')

        self.run_spider(last_date, spidercls)

        # we drop the table and insert all the data again
        cursor.execute(f'DROP TABLE {spider_name} CASCADE ;')
        self.create_table(cursor, spider_name)

        data_directory = os.path.join(self.settings['FILES_STORE'], f'{spider_name}', FOLDER_NAME)

        logger.info('Starting the compile/file reading process')
        if opts.compile:
            csv_file_name = self.json_to_csv(merge(self.get_data_from_directory(data_directory)),
                                             data_directory)
        # if we don't need to compile the releases, we insert them directly in the database
        else:
            if 'release' in spidercls.data_type:
                list_type = 'releases.item'
            else:
                list_type = 'records.item.compiledRelease'
            csv_file_name = self.json_to_csv(self.get_data_from_directory(data_directory, list_type),
                                             data_directory)
        logger.info('Dumping the data into the data base')
        with open(csv_file_name) as csv_file:
            cursor.copy_expert(f"COPY {spider_name}(data) FROM STDIN WITH CSV", csv_file)
        os.remove(csv_file_name)
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{spider_name} ON {spider_name}(cast(data->>'date' as text));")
        connection.commit()

        logger.info('Process completed')
