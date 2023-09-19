import csv
import os
from datetime import datetime

import ijson
import psycopg2.sql
from ocdskit.combine import merge
from scrapy import signals
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy import util
from kingfisher_scrapy.extensions.files_store import FilesStore


class DatabaseStore:
    """
    If the ``DATABASE_URL`` Scrapy setting and the ``crawl_time`` spider argument are set, the OCDS data is stored in a
    PostgreSQL database, incrementally.

    This extension stores data in the "data" column of a table named after the spider, or the ``table_name`` spider
    argument (if set). When the spider is opened, if the table doesn't exist, it is created. The spider's ``from_date``
    attribute is then set, in order of precedence, to: the ``from_date`` spider argument (unless equal to the spider's
    ``default_from_date`` class attribute); the maximum value of the ``date`` field of the stored data (if any); the
    spider's ``default_from_date`` class attribute (if set).

    When the spider is closed, this extension reads the data written by the FilesStore extension to the crawl directory
    that matches the ``crawl_time`` spider argument. If the ``compile_releases`` spider argument is set, it creates
    compiled releases, using individual releases. Then, it recreates the table, and inserts either the compiled
    releases if the ``compile_releases`` spider argument is set, the individual releases in release packages (if the
    spider returns releases), or the compiled releases in record packages (if the spider returns records).

    .. warning::

       If the ``compile_releases`` spider argument is set, spiders that return records without embedded releases are
       not supported. If it isn't set, then spiders that return records without compiled releases are not supported.

    To perform incremental updates, the OCDS data in the crawl directory must not be deleted between crawls.
    """

    def __init__(self, database_url, files_store_directory):
        self.database_url = database_url
        self.files_store_directory = files_store_directory

        self.connection = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        database_url = crawler.settings['DATABASE_URL']
        directory = crawler.settings['FILES_STORE']

        if not database_url:
            raise NotConfigured('DATABASE_URL is not set.')
        if not directory:
            raise NotConfigured('FILES_STORE is not set.')

        extension = cls(database_url, directory)

        crawler.signals.connect(extension.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(extension.spider_closed, signal=signals.spider_closed)

        return extension

    def spider_opened(self, spider):
        self.connection = psycopg2.connect(self.database_url)
        self.cursor = self.connection.cursor()
        try:
            table_name = self.get_table_name(spider)
            self.create_table(table_name)

            # If there is not a from_date from the command line or the from_date is equal to the default_from_date,
            # get the most recent date in the spider's data table.
            if getattr(spider, 'default_from_date', None):
                default_from_date = datetime.strptime(spider.default_from_date, spider.date_format)
            else:
                default_from_date = None

            if not spider.from_date or spider.from_date == default_from_date:
                spider.logger.info('Getting the date from which to resume the crawl from the %s table', table_name)
                self.execute("SELECT max(data->>'date')::timestamptz FROM {table}", table=table_name)
                from_date = self.cursor.fetchone()[0]
                if from_date:
                    formatted_from_date = datetime.strftime(from_date, spider.date_format)
                    spider.logger.info('Resuming the crawl from %s', formatted_from_date)
                    spider.from_date = datetime.strptime(formatted_from_date, spider.date_format)

            self.connection.commit()
        finally:
            self.cursor.close()
            self.connection.close()

    def spider_closed(self, spider, reason):
        if reason not in ('finished', 'sample'):
            return

        if spider.database_store_compile_releases:
            if 'release' in spider.data_type:
                prefix = ''
            else:
                prefix = 'records.item.releases.item'
        elif 'release' in spider.data_type:
            prefix = 'releases.item'
        else:
            prefix = 'records.item.compiledRelease'

        crawl_directory = os.path.join(self.files_store_directory, FilesStore.relative_crawl_directory(spider))
        spider.logger.info('Reading the %s crawl directory with the %s prefix', crawl_directory, prefix or 'empty')
        table_name = self.get_table_name(spider)

        data = self.yield_items_from_directory(crawl_directory, prefix)
        if spider.database_store_compile_releases:
            spider.logger.info('Creating generator of compiled releases')
            data = merge(data)

        filename = os.path.join(crawl_directory, 'data.csv')
        spider.logger.info('Writing the JSON data to the %s CSV file', filename)
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            for item in data:
                writer.writerow([util.json_dumps(item, ensure_ascii=False).replace(r'\u0000', '')])

        spider.logger.info('Replacing the JSON data in the %s table', table_name)
        self.connection = psycopg2.connect(self.database_url)
        self.cursor = self.connection.cursor()
        try:
            self.execute('DROP TABLE {table}', table=table_name)
            self.create_table(table_name)
            with open(filename) as f:
                self.cursor.copy_expert(self.format('COPY {table}(data) FROM STDIN WITH CSV', table=table_name), f)
            self.execute("CREATE INDEX {index} ON {table}(cast(data->>'date' as text))", table=table_name,
                         index=f'idx_{table_name}')
            self.connection.commit()
        finally:
            self.cursor.close()
            self.connection.close()
            os.remove(filename)

    def create_table(self, table):
        self.execute('CREATE TABLE IF NOT EXISTS {table} (data jsonb)', table=table)

    def yield_items_from_directory(self, crawl_directory, prefix=''):
        for dir_entry in os.scandir(crawl_directory):
            if dir_entry.name.endswith('.json'):
                with open(dir_entry.path, 'rb') as f:
                    yield from ijson.items(f, prefix)

    # Copied from kingfisher-summarize
    def format(self, statement, **kwargs):
        """
        Formats the SQL statement, expressed as a format string with keyword arguments. A keyword argument's value is
        converted to a SQL identifier, or a list of SQL identifiers, unless it's already a ``sql`` object.
        """
        objects = {}
        for key, value in kwargs.items():
            if isinstance(value, psycopg2.sql.Composable):
                objects[key] = value
            elif isinstance(value, list):
                objects[key] = psycopg2.sql.SQL(', ').join(psycopg2.sql.Identifier(entry) for entry in value)
            else:
                objects[key] = psycopg2.sql.Identifier(value)
        return psycopg2.sql.SQL(statement).format(**objects)

    # Copied from kingfisher-summarize
    def execute(self, statement, variables=None, **kwargs):
        """
        Executes the SQL statement.
        """
        if kwargs:
            statement = self.format(statement, **kwargs)
        self.cursor.execute(statement, variables)

    def get_table_name(self, spider):
        return spider.database_store_table_name if spider.database_store_table_name else spider.name
