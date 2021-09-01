# https://docs.scrapy.org/en/latest/topics/extensions.html#writing-your-own-extension
import csv
import json
import os
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit

import ijson
import pika
import psycopg2
import requests
import sentry_sdk
from ocdskit.combine import merge
from psycopg2 import sql
from scrapy import signals
from scrapy.exceptions import NotConfigured, StopDownload
from twisted.python.failure import Failure

from kingfisher_scrapy import util
from kingfisher_scrapy.items import File, FileError, FileItem, PluckedItem
from kingfisher_scrapy.kingfisher_process import Client


# https://docs.scrapy.org/en/latest/topics/extensions.html#writing-your-own-extension
class Pluck:
    """
    Appends one data value from one plucked item to a file. See the :ref:`pluck` command.
    """

    def __init__(self, directory, max_bytes):
        self.directory = directory
        self.max_bytes = max_bytes

        # The number of bytes received.
        self.total_bytes_received = 0
        # Whether `item_scraped` has been called.
        self.item_scraped_called = False

    @classmethod
    def from_crawler(cls, crawler):
        directory = crawler.settings['KINGFISHER_PLUCK_PATH']
        max_bytes = crawler.settings['KINGFISHER_PLUCK_MAX_BYTES']

        extension = cls(directory=directory, max_bytes=max_bytes)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(extension.spider_closed, signal=signals.spider_closed)
        if max_bytes:
            crawler.signals.connect(extension.bytes_received, signal=signals.bytes_received)

        return extension

    def bytes_received(self, data, request, spider):
        if (
            not spider.pluck
            or spider.dont_truncate
            # We only limit bytes received for final requests (i.e. where the callback is the default `parse` method).
            or request.callback
            # ijson will parse the value at `root_path`, which can go to the end of the file.
            # https://github.com/ICRAR/ijson/issues/43
            or spider.root_path
            # XLSX files must be read in full.
            or spider.unflatten
        ):
            return

        self.total_bytes_received += len(data)
        if self.total_bytes_received >= self.max_bytes:
            raise StopDownload(fail=False)

    def item_scraped(self, item, spider):
        if not spider.pluck or self.item_scraped_called or not isinstance(item, PluckedItem):
            return

        self.item_scraped_called = True

        self._write(spider, item['value'])

    def spider_closed(self, spider, reason):
        if not spider.pluck or self.item_scraped_called:
            return

        self._write(spider, f'closed: {reason}')

    def _write(self, spider, value):
        with open(os.path.join(self.directory, util.pluck_filename(spider)), 'a+') as f:
            f.write(f'{value},{spider.name}\n')


class FilesStore:
    """
    Writes items' data to individual files in a directory. See the :ref:`how-it-works` documentation.
    """

    def __init__(self, directory):
        self.directory = directory

    @classmethod
    def relative_crawl_directory(cls, spider):
        """
        Returns the crawl's relative directory, in the format `<spider_name>[_sample]/<YYMMDD_HHMMSS>`.
        """
        spider_directory = spider.name
        if spider.sample:
            spider_directory += '_sample'

        return os.path.join(spider_directory, spider.get_start_time('%Y%m%d_%H%M%S'))

    @classmethod
    def from_crawler(cls, crawler):
        directory = crawler.settings['FILES_STORE']

        if not directory:
            raise NotConfigured('FILES_STORE is not set.')

        extension = cls(directory)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)

        return extension

    def spider_opened(self, spider):
        if hasattr(spider, '_job'):
            path = os.path.join(self.relative_crawl_directory(spider), 'scrapyd-job.txt')
            self._write_file(path, spider._job)

    def item_scraped(self, item, spider):
        """
        If the item is a File or FileItem, writes its data to the filename in the crawl's directory.

        Returns a dict with the metadata.
        """
        if not isinstance(item, (File, FileItem)):
            return

        file_name = item['file_name']
        if isinstance(item, FileItem):
            name, extension = util.get_file_name_and_extension(file_name)
            file_name = f"{name}-{item['number']}.{extension}"

        path = os.path.join(self.relative_crawl_directory(spider), file_name)
        self._write_file(path, item['data'])

        item['path'] = path
        item['files_store'] = self.directory

    def _write_file(self, path, data):
        path = os.path.join(self.directory, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if isinstance(data, bytes):
            mode = 'wb'
        else:
            mode = 'w'

        with open(path, mode) as f:
            if isinstance(data, (bytes, str)):
                f.write(data)  # NOTE: needs to be UTF-8
            else:
                util.json_dump(data, f)


class DatabaseStore:
    """
    If the ``DATABASE_URL`` Scrapy setting and the ``crawl_time`` spider argument are set, the OCDS data is stored in a
    PostgresSQL database, incrementally.

    This extension stores data in the "data" column of a table named after the spider. When the spider is opened, if
    the table doesn't exist, it is created. The spider's ``from_date`` attribute is then set, in order of precedence,
    to: the ``from_date`` spider argument (unless equal to the spider's ``default_from_date`` class attribute); the
    maximum value of the ``date`` field of the stored data (if any); the spider's ``default_from_date`` class attribute
    (if set).

    When the spider is closed, this extension reads the data written by the FilesStore extension to the crawl directory
    that matches the ``crawl_time`` spider argument. If the ``compile_releases`` spider argument is set, it creates
    compiled releases. Then, it recreates the table, and inserts either the compiled releases, the individual releases
    in release packages (if the spider returns releases), or the compiled releases in record packages (if the spider
    returns records). (Spiders that return records without ``compiledRelease`` fields are not supported.)

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
            self.create_table(spider.name)

            # If there is not a from_date from the command line or the from_date is equal to the default_from_date,
            # get the most recent date in the spider's data table.
            if getattr(spider, 'default_from_date', None):
                default_from_date = datetime.strptime(spider.default_from_date, spider.date_format)
            else:
                default_from_date = None

            if not spider.from_date or spider.from_date == default_from_date:
                spider.logger.info('Getting the date from which to resume the crawl from the %s table', spider.name)
                self.execute("SELECT max(data->>'date')::timestamptz FROM {table}", table=spider.name)
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

        if spider.compile_releases:
            prefix = ''
        elif 'release' in spider.data_type:
            prefix = 'releases.item'
        else:
            prefix = 'records.item.compiledRelease'

        crawl_directory = os.path.join(self.files_store_directory, FilesStore.relative_crawl_directory(spider))
        spider.logger.info('Reading the %s crawl directory with the %s prefix', crawl_directory, prefix or 'empty')

        data = self.yield_items_from_directory(crawl_directory, prefix)
        if spider.compile_releases:
            spider.logger.info('Creating compiled releases')
            data = merge(data)

        filename = os.path.join(crawl_directory, 'data.csv')
        spider.logger.info('Writing the JSON data to the %s CSV file', filename)
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            for item in data:
                writer.writerow([util.json_dumps(item)])

        spider.logger.info('Replacing the JSON data in the %s table', spider.name)
        self.connection = psycopg2.connect(self.database_url)
        self.cursor = self.connection.cursor()
        try:
            self.execute('DROP TABLE {table}', table=spider.name)
            self.create_table(spider.name)
            with open(filename) as f:
                self.cursor.copy_expert(self.format('COPY {table}(data) FROM STDIN WITH CSV', table=spider.name), f)
            self.execute("CREATE INDEX {index} ON {table}(cast(data->>'date' as text))", table=spider.name,
                         index=f'idx_{spider.name}')
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


class ItemCount:
    """
    Adds a count to the crawl stats for each type of item scraped.
    """

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        extension = cls(crawler.stats)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)
        return extension

    def item_scraped(self, item, spider):
        self.stats.inc_value(f'{type(item).__name__.lower()}_count')


class KingfisherProcessAPI:
    """
    If the ``KINGFISHER_API_URI`` and ``KINGFISHER_API_KEY`` environment variables or configuration settings are set,
    then messages are sent to a Kingfisher Process API for the ``item_scraped`` and ``spider_closed`` signals.
    """

    def __init__(self, url, key, directory=None):
        """
        Initializes a Kingfisher Process API client.
        """
        self.client = Client(url, key)
        self.directory = directory

    @classmethod
    def from_crawler(cls, crawler):
        url = crawler.settings['KINGFISHER_API_URI']
        key = crawler.settings['KINGFISHER_API_KEY']
        directory = crawler.settings['KINGFISHER_API_LOCAL_DIRECTORY']

        if not url or not key:
            raise NotConfigured('KINGFISHER_API_URI and/or KINGFISHER_API_KEY is not set.')

        if crawler.settings['DATABASE_URL']:
            raise NotConfigured('DATABASE_URL is set.')

        extension = cls(url, key, directory=directory)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(extension.item_error, signal=signals.item_error)
        crawler.signals.connect(extension.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(extension.spider_error, signal=signals.spider_error)

        return extension

    def spider_closed(self, spider, reason):
        """
        Sends an API request to end the collection's store step.
        """
        # https://docs.scrapy.org/en/latest/topics/signals.html#spider-closed
        if reason not in ('finished', 'sample') or spider.pluck or spider.keep_collection_open:
            return

        data = self._build_data_to_send(spider)
        return self._request(spider, 'end_collection_store', data['collection_source'], data)

    def spider_error(self, failure, response, spider):
        """
        Sends an API request to store a file error in Kingfisher Process when a spider callback generates an error.
        """
        # https://docs.scrapy.org/en/latest/topics/signals.html#scrapy.signals.spider_error
        file_name = response.request.meta.get('file_name', response.request.url)
        data = self._build_data_to_send(spider, file_name, response.request.url, errors=failure)
        return self._request(spider, 'create_file_error', response.request.url, data)

    def item_error(self, item, response, spider, failure):
        """
        Sends an API request to store a file error in Kingfisher Process when a item pipeline generates an error.
        """
        # https://docs.scrapy.org/en/latest/topics/signals.html#scrapy.signals.item_error
        data = self._build_data_to_send(spider, item['file_name'], item['url'], errors=failure)
        return self._request(spider, 'create_file_error', item['file_name'], data)

    def item_scraped(self, item, spider):
        """
        Sends an API request to store the file, file item or file error in Kingfisher Process.
        """
        # https://docs.scrapy.org/en/latest/topics/signals.html#scrapy.signals.item_scraped
        if isinstance(item, PluckedItem):
            return

        data = self._build_data_to_send(spider, item['file_name'], item['url'])

        if isinstance(item, FileError):
            data['errors'] = json.dumps(item['errors'])

            return self._request(spider, 'create_file_error', item['url'], data)

        data['data_type'] = item['data_type']
        data['encoding'] = spider.encoding
        if spider.note:
            data['collection_note'] = spider.note

        if isinstance(item, FileItem):
            data['number'] = item['number']
            if isinstance(item['data'], (bytes, str)):
                data['data'] = item['data']
            else:
                data['data'] = util.json_dumps(item['data'])

            return self._request(spider, 'create_file_item', item['url'], data)

        # File
        if self.directory:
            path = item['path']
            data['local_file_name'] = os.path.join(self.directory, path)
            files = {}
        else:
            path = os.path.join(item['files_store'], item['path'])
            f = open(path, 'rb')
            files = {'file': (item['file_name'], 'application/json', f)}

        return self._request(spider, 'create_file', item['url'], data, files)

    def _request(self, spider, method, infix, *args):
        def log_for_status(response):
            # Same condition as `Response.raise_for_status` in requests module.
            # https://github.com/psf/requests/blob/28cc1d237b8922a2dcbd1ed95782a7f1751f475b/requests/models.py#L920
            if 400 <= response.code < 600:
                spider.logger.warning('%s failed (%s) with status code: %d', method, infix, response.code)
            # A return value is provided to ease testing.
            return response

        d = getattr(self.client, method)(*args)
        d.addCallback(log_for_status)
        return d

    @staticmethod
    def _build_data_to_send(spider, file_name=None, url=None, errors=None):
        data = {
            'collection_source': spider.name,
            'collection_data_version': spider.get_start_time('%Y-%m-%d %H:%M:%S'),
            'collection_sample': str(bool(spider.sample)),
            'collection_ocds_version': spider.ocds_version,
        }
        if file_name:
            data['file_name'] = file_name
        if url:
            data['url'] = url
        if errors:
            # https://twistedmatrix.com/documents/current/api/twisted.python.failure.Failure.html
            if isinstance(errors, Failure):
                errors = {'twisted': str(errors)}
            data['errors'] = json.dumps(errors)
        return data


class KingfisherProcessAPI2:
    """
    If the ``KINGFISHER_API2_URL`` environment variable or configuration setting is set,
    then messages are sent to a Kingfisher Process API for the ``item_scraped`` and ``spider_closed`` signals.
    """

    ITEMS_SENT_POST = 'kingfisher_process_items_sent_post'
    ITEMS_FAILED_POST = 'kingfisher_process_items_failed_post'

    ITEMS_SENT_RABBIT = 'kingfisher_process_items_sent_rabbit'
    ITEMS_FAILED_RABBIT = 'kingfisher_process_items_failed_rabbit'

    def __init__(self, url, stats, rabbit_url=None, rabbit_exchange_name=None, rabbit_routing_key=None):
        self.url = url
        self.stats = stats
        self.rabbit_url = rabbit_url
        self.rabbit_exchange_name = rabbit_exchange_name
        self.rabbit_routing_key = rabbit_routing_key

        # The collection ID is set by the spider_opened handler.
        self.collection_id = None

        if rabbit_url:
            self.channel = self._get_rabbit_channel()
        else:
            self.channel = None

    @classmethod
    def from_crawler(cls, crawler):
        url = crawler.settings['KINGFISHER_API2_URL']
        rabbit_url = crawler.settings['RABBIT_URL']
        rabbit_exchange_name = crawler.settings['RABBIT_EXCHANGE_NAME']
        rabbit_routing_key = crawler.settings['RABBIT_ROUTING_KEY']

        if not url:
            raise NotConfigured('KINGFISHER_API2_URL is not set.')

        if crawler.settings['DATABASE_URL']:
            raise NotConfigured('DATABASE_URL is set.')

        extension = cls(url, crawler.stats, rabbit_url, rabbit_exchange_name, rabbit_routing_key)
        crawler.signals.connect(extension.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(extension.spider_closed, signal=signals.spider_closed)

        return extension

    def spider_opened(self, spider):
        """
        Sends an API request to create a collection in Kingfisher Process.
        """
        data = {
            'source_id': spider.name,
            'data_version': spider.get_start_time('%Y-%m-%d %H:%M:%S'),
            'sample': bool(spider.sample),
            'note': spider.note,
            'job': getattr(spider, '_job', None),
            'upgrade': spider.ocds_version == '1.0',
        }

        for step in spider.steps:
            data[step] = True

        # This request must be synchronous, to have the collection ID for the item_scraped handler.
        response = self._post_synchronous(spider, 'api/v1/create_collection', data)

        if response.ok:
            self.collection_id = response.json()['collection_id']
            spider.logger.info('Created collection %d in Kingfisher Process', self.collection_id)
        else:
            spider.logger.error('Failed to create collection. API status code: %d', response.status_code)

    def spider_closed(self, spider, reason):
        """
        Sends an API request to close the collection in Kingfisher Process.
        """
        if spider.pluck or spider.keep_collection_open:
            return

        if not self.collection_id:
            return

        response = self._post_synchronous(spider, 'api/v1/close_collection', {
            'collection_id': self.collection_id,
            'reason': reason,
            'stats': json.loads(json.dumps(self.stats.get_stats(), default=str))  # for datetime objects
        })

        if response.ok:
            spider.logger.info('Closed collection %d in Kingfisher Process', self.collection_id)
        else:
            spider.logger.error('Failed to close collection. API status code: %d', response.status_code)

    def item_scraped(self, item, spider):
        """
        Sends either a RabbitMQ or API request to store the file, file item or file error in Kingfisher Process.
        """
        if isinstance(item, PluckedItem):
            return

        if not self.collection_id:
            return

        data = {
            'collection_id': self.collection_id,
            'url': item['url'],
        }

        if isinstance(item, FileError):
            data['errors'] = json.dumps(item['errors'])
        else:
            data['path'] = os.path.abspath(os.path.join(item['files_store'], item['path']))

        if self.rabbit_url:
            try:
                self._publish_to_rabbit(data)
                self.stats.inc_value(self.ITEMS_SENT_RABBIT)
            except Exception as e:
                self.stats.inc_value(self.ITEMS_FAILED_RABBIT)
                spider.logger.error('Failed to publish message to RabbitMQ: %s', e)
        else:
            response = self._post_synchronous(spider, 'api/v1/create_collection_file', data)
            if response.ok:
                self.stats.inc_value(self.ITEMS_SENT_POST)
                spider.logger.debug('Created collection file in Kingfisher Process')
            else:
                self.stats.inc_value(self.ITEMS_FAILED_POST)
                spider.logger.error('Failed to create collection file. API status code: %d', response.status_code)

    def _post_synchronous(self, spider, path, data):
        """
        POSTs synchronous API requests to Kingfisher Process.
        """
        url = urljoin(self.url, path)
        spider.logger.debug('Sending synchronous request to Kingfisher Process at %s with %s', url, data)
        return requests.post(url, json=data)

    # This method is extracted so that it can be mocked in tests.
    def _publish_to_rabbit(self, message):
        self.channel.basic_publish(
            exchange=self.rabbit_exchange_name,
            routing_key=self.rabbit_routing_key,
            body=json.dumps(message),
            # https://www.rabbitmq.com/publishers.html#message-properties
            properties=pika.BasicProperties(delivery_mode=2, content_type='application/json')
        )

    # This method is extracted so that it can be mocked in tests.
    def _get_rabbit_channel(self):
        parsed = urlsplit(self.rabbit_url)
        query = parse_qs(parsed.query)
        # NOTE: Heartbeat should not be disabled.
        # https://github.com/open-contracting/data-registry/issues/140
        query.update({'blocked_connection_timeout': 1800, 'heartbeat': 0})

        connection = pika.BlockingConnection(pika.URLParameters(parsed._replace(query=urlencode(query)).geturl()))

        channel = connection.channel()
        channel.exchange_declare(exchange=self.rabbit_exchange_name, durable=True, exchange_type='direct')

        return channel


# https://stackoverflow.com/questions/25262765/handle-all-exception-in-scrapy-with-sentry
class SentryLogging:
    """
    Sends exceptions and log records to Sentry. Log records with a level of ``ERROR`` or higher are captured as events.

    https://docs.sentry.io/platforms/python/logging/
    """

    @classmethod
    def from_crawler(cls, crawler):
        sentry_dsn = crawler.settings.get('SENTRY_DSN', None)
        if sentry_dsn is None:
            raise NotConfigured
        extension = cls()
        sentry_sdk.init(sentry_dsn)
        return extension
