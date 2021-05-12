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
        return '[options] <spider> <database-schema> <crawl-time>'

    def short_desc(self):
        return 'Download OCDS data and store it in a PostgresSQL database, incrementally'

    def long_desc(self):
        return "Download OCDS data and store it in a PostgresSQL database. The database schema must already exist. " \
               "A table with a \"data\" column is created if it doesn't exist, named after the spider. If the table " \
               "isn't empty, the crawl starts with the `from_date` spider argument set to the maximum value of the " \
               "`date` field of the OCDS data stored in the \"data\" column. If the spider returns records, each " \
               "record must set the `compiledRelease` field."

    def add_options(self, parser):
        ScrapyCommand.add_options(self, parser)
        parser.add_option('--compile', action='store_true',
                          help='Merge individual releases into compiled releases')

    def format_from_date(self, date, date_format):
        if date_format == 'datetime':
            return date[:19]
        if date_format == 'date':
            return date[:10]
        if date_format == 'year-month':
            return date[:7]
        return date[:4]

    # Copied from kingfisher-summarize
    def format(self, statement, **kwargs):
        """
        Formats the SQL statement, expressed as a format string with keyword arguments. A keyword argument's value is
        converted to a SQL identifier, or a list of SQL identifiers, unless it's already a ``sql`` object.
        """
        objects = {}
        for key, value in kwargs.items():
            if isinstance(value, sql.Composable):
                objects[key] = value
            elif isinstance(value, list):
                objects[key] = sql.SQL(', ').join(sql.Identifier(entry) for entry in value)
            else:
                objects[key] = sql.Identifier(value)
        return sql.SQL(statement).format(**objects)

    # Copied from kingfisher-summarize
    def execute(self, statement, variables=None, **kwargs):
        """
        Executes the SQL statement.
        """
        if kwargs:
            statement = self.format(statement, **kwargs)
        self.cursor.execute(statement, variables)

    def create_table(self, table):
        self.execute('CREATE TABLE IF NOT EXISTS {table} (data jsonb)', table=table)

    def yield_items_from_directory(self, data_directory, prefix=''):
        for dir_entry in os.scandir(data_directory):
            if dir_entry.name.endswith('.json'):
                with open(dir_entry.path) as f:
                    yield from ijson.items(f, prefix)

    def run(self, args, opts):
        # Check the settings and environment.
        if not self.settings['FILES_STORE'] or not os.getenv('KINGFISHER_COLLECT_DATABASE_URL'):
            raise NotConfigured('FILES_STORE and/or KINGFISHER_COLLECT_DATABASE_URL is not set.')

        # Check the command-line arguments.
        if len(args) < 3:
            raise UsageError('The spider, database-schema and crawl-time arguments must be set.')

        spider_name = args[0]
        schema_name = args[1]
        crawl_time = args[2]

        try:
            spidercls = self.crawler_process.spider_loader.load(spider_name)
        except KeyError:
            raise UsageError(f'The spider argument {spider_name!r} is not a known spider.')

        try:
            crawl_directory = datetime.datetime.strptime(crawl_time, '%Y-%m-%dT%H:%M:%S').strftime('%Y%m%d_%H%M%S')
        except ValueError as e:
            raise UsageError(f'The crawl-time argument {crawl_time!r} must be in YYYY-MM-DDTHH:MM:SS format: {e}')

        if opts.compile and 'record' in spidercls.data_type:
            raise UsageError('The --compile flag can be set only if the spider returns releases.')

        logger.info('Getting the date from which to resume the crawl (if any)')

        # Create the database connection.
        self.connection = psycopg2.connect(os.getenv('KINGFISHER_COLLECT_DATABASE_URL'))
        self.cursor = self.connection.cursor()
        self.execute('SET search_path = {schema}', schema=schema_name)

        # Get the most recent date in the spider's data table.
        self.create_table(spider_name)
        self.execute("SELECT max(data->>'date') FROM {table}", table=spider_name)
        from_date = self.cursor.fetchone()[0]

        # Set the spider arguments.
        kwargs = {'crawl_time': crawl_time}
        if from_date:
            kwargs['from_date'] = self.format_from_date(from_date, spidercls.date_format)

        logger.info(f"Running: scrapy crawl {spider_name} {' '.join(f'-a {key}={value}' for key, value in kwargs)}")

        # Run the crawl, without sending data to Kingfisher Process.
        self.settings['EXTENSIONS']['kingfisher_scrapy.extensions.KingfisherProcessAPI'] = None
        self.crawler_process.crawl(spidercls, **kwargs)
        self.crawler_process.start()

        logger.info('Reading the crawl directory')

        if opts.compile:
            list_type = ''
        elif 'release' in spidercls.data_type:
            list_type = 'releases.item'
        else:
            list_type = 'records.item.compiledRelease'

        crawl_directory_full_path = os.path.join(self.settings['FILES_STORE'], spider_name, crawl_directory)
        data = self.yield_items_from_directory(crawl_directory_full_path, list_type)

        if opts.compile:
            logger.info('Creating compiled releases')
            data = merge(data)

        logger.info('Writing the JSON data to a CSV file')

        filename = os.path.join(crawl_directory_full_path, 'data.csv')
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            for item in data:
                writer.writerow([json.dumps(item, default=util.default)])

        logger.info('Replacing the JSON data in the SQL table')

        try:
            self.execute('DROP TABLE {table} CASCADE', table=spider_name)
            self.create_table(spider_name)
            with open(filename) as f:
                self.cursor.copy_expert(self.format('COPY {table}(data) FROM STDIN WITH CSV', table=spider_name), f)
            self.execute("CREATE INDEX idx_{table} ON {table}(cast(data->>'date' as text))", table=spider_name)
            self.connection.commit()
        finally:
            self.cursor.close()
            self.connection.close()
            os.remove(filename)
