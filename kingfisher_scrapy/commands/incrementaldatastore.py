import csv
import datetime
import json
import os

import ijson
import psycopg2
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError, NotConfigured

from kingfisher_scrapy import util

# these can be a command line argument as well
CRAWL_TIME = '2021-04-22T00:00:00'
FOLDER_NAME = datetime.datetime.strptime(CRAWL_TIME, '%Y-%m-%dT%H:%M:%S').strftime('%Y%m%d_%H%M%S')
# currently, the command assumes that the given schema exists
SCHEMA_NAME = 'bi'


class IncrementalDataStore(ScrapyCommand):
    def syntax(self):
        return '[options] spider'

    def short_desc(self):
        return 'Store compile releases from the given spider in a PostgresSQL database, incrementally'

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option('--spider', type=str, help='The spider to run')
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

    def database_setup(self, spider_name):
        """
        Creates the database connection, set the search path and create the required table if doesn't exists.
        """
        connection = psycopg2.connect(os.getenv('KINGFISHER_COLLECT_DATABASE_URL'))
        cursor = connection.cursor()
        cursor.execute(f'SET search_path = {SCHEMA_NAME}')
        self.create_table(cursor, spider_name)
        return connection, cursor

    def create_table(self, cursor, spider_name):
        """
        Creates a table with a jsonb "data" column and creates and index on the data->>'date' field
        """
        cursor.execute(f'CREATE TABLE IF NOT EXISTS {spider_name} (data jsonb);')
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{spider_name} ON {spider_name}(cast(data->>'date' as text));")

    def run_spider(self, last_date, spidercls):

        if not self.settings['FILES_STORE'] or not os.getenv('KINGFISHER_COLLECT_DATABASE_URL'):
            raise NotConfigured('You must set a FILES_STORE and KINGFISHER_COLLECT_DATABASE_URL')

        kwargs = {'crawl_time': CRAWL_TIME}


        # If there is data already in the database we only download data after the last release date
        if last_date:
            kwargs['from_date'] = self.from_date_formatted(last_date, spidercls.date_format)
        self.crawler_process.crawl(spidercls, **kwargs)
        self.crawler_process.start()

    def json_to_csv(self, data_directory):
        """
        Reads all the OCDS release packages json files from the given directory and save each release as a row in a
        csv file called data.csv
        """
        file_name = os.path.join(data_directory, 'data.csv')
        with open(file_name, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            for filename in os.listdir(data_directory):
                if filename.endswith('.json'):
                    with open(os.path.join(data_directory, filename)) as f:
                        for item in ijson.items(f, 'releases.item'):
                            data = json.dumps(item, default=util.default)
                            csv_writer.writerow([data])
        return file_name

    def run(self, args, opts):
        spiders = self.crawler_process.spider_loader.list()
        spider_name = opts.spider

        if not spider_name or opts.spider not in spiders:
            raise UsageError('A valid spider must be given.')

        spidercls = self.crawler_process.spider_loader.load(spider_name)

        # we disable kingfisher process extension
        self.settings['EXTENSIONS']['kingfisher_scrapy.extensions.KingfisherProcessAPI'] = None

        connection, cursor = self.database_setup(spider_name)

        # gets the last data->>'date' that exists in the country table
        cursor.execute(f"SELECT max(data->>'date') FROM {spider_name};")
        last_date = cursor.fetchone()[0]

        self.run_spider(last_date, spider_name)

        # we drop the table and insert all the data again
        cursor.execute(f'DROP TABLE {spider_name} CASCADE ;')
        self.create_table(cursor, spider_name)

        data_directory = os.path.join(self.settings['FILES_STORE'], f'{spider_name}', FOLDER_NAME)
        # if we don't need to compile the releases, we insert them directly in the database
        if opts.compile:
            raise NotImplementedError('The compile option is not implemented yet')
        else:
            csv_file_name = self.json_to_csv(data_directory)
            with open(csv_file_name) as csv_file:
                cursor.copy_expert(f"COPY {spider_name}(data) FROM STDIN WITH CSV", csv_file)
            os.remove(csv_file_name)
            connection.commit()
