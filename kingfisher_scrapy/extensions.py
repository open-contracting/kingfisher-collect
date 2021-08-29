# https://docs.scrapy.org/en/latest/topics/extensions.html#writing-your-own-extension
import csv
import json
import logging
import os
from datetime import datetime

import ijson
import psycopg2
import requests
import sentry_sdk
from ocdskit.combine import merge
from pika import BasicProperties, BlockingConnection, ConnectionParameters, PlainCredentials
from psycopg2 import sql
from scrapy import signals
from scrapy.exceptions import NotConfigured, StopDownload
from twisted.python.failure import Failure

from kingfisher_scrapy import util
from kingfisher_scrapy.items import File, FileError, FileItem, PluckedItem
from kingfisher_scrapy.kingfisher_process import Client
from kingfisher_scrapy.util import _pluck_filename, get_file_name_and_extension


# https://docs.scrapy.org/en/latest/topics/extensions.html#writing-your-own-extension
class Pluck:
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
        with open(os.path.join(self.directory, _pluck_filename(spider)), 'a+') as f:
            f.write(f'{value},{spider.name}\n')


class FilesStore:
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
    def absolute_crawl_directory(cls, spider, files_store_directory):
        """
        Returns the crawl's absolute directory.
        """
        return os.path.join(files_store_directory, cls.relative_crawl_directory(spider))

    @classmethod
    def from_crawler(cls, crawler):
        directory = crawler.settings['FILES_STORE']

        if not directory:
            raise NotConfigured('FILES_STORE is not set.')

        extension = cls(directory)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)

        return extension

    def item_scraped(self, item, spider):
        """
        If the item is a File or FileItem, writes its data to the filename in the crawl's directory.

        Returns a dict with the metadata.
        """
        if not isinstance(item, (File, FileItem)):
            return

        file_name = item['file_name']
        if isinstance(item, FileItem):
            name, extension = get_file_name_and_extension(file_name)
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
                f.write(data)
            else:
                json.dump(data, f, default=util.default)


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

    connection = None
    cursor = None
    files_store_directory = None

    logger = logging.getLogger(__name__)

    def __init__(self, database_url, files_store_directory):
        self.database_url = database_url
        self.files_store_directory = files_store_directory

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
                self.logger.info(f'Getting the date from which to resume the crawl from the {spider.name} table')
                self.execute("SELECT max(data->>'date')::timestamptz FROM {table}", table=spider.name)
                from_date = self.cursor.fetchone()[0]
                if from_date:
                    formatted_from_date = datetime.strftime(from_date, spider.date_format)
                    self.logger.info(f'Resuming the crawl from {formatted_from_date}')
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

        crawl_directory = FilesStore.absolute_crawl_directory(spider, self.files_store_directory)
        self.logger.info(f"Reading the {crawl_directory} crawl directory with the {prefix or 'empty'} prefix")

        data = self.yield_items_from_directory(crawl_directory, prefix)
        if spider.compile_releases:
            self.logger.info('Creating compiled releases')
            data = merge(data)

        filename = os.path.join(crawl_directory, 'data.csv')
        self.logger.info(f'Writing the JSON data to the {filename} CSV file')
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            for item in data:
                writer.writerow([json.dumps(item, default=util.default)])

        self.logger.info(f'Replacing the JSON data in the {spider.name} table')
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
                with open(dir_entry.path) as f:
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
        data['encoding'] = item.get('encoding', 'utf-8')
        if spider.note:
            data['collection_note'] = spider.note

        if isinstance(item, FileItem):
            data['number'] = item['number']
            if isinstance(item['data'], (str, bytes)):
                data['data'] = item['data']
            else:
                data['data'] = json.dumps(item['data'], default=util.default)

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
                spider.logger.warning(f'{method} failed ({infix}) with status code: {response.code}')
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


class KingfisherProcessAPI2:
    ITEMS_SENT_KEY_POST = "kingfisher_process_items_sent_post"
    ITEMS_FAILED_KEY_POST = "kingfisher_process_items_failed_post"

    ITEMS_SENT_KEY_RABBIT = "kingfisher_process_items_sent_rabbit"
    ITEMS_FAILED_KEY_RABBIT = "kingfisher_process_items_failed_rabbit"

    """
    If the ``KINGFISHER_API2_URL`` environment variable or configuration setting is set,
    then messages are sent to a Kingfisher Process API for the ``item_scraped`` and ``spider_closed`` signals.
    """
    def __init__(self,
                 url,
                 username,
                 password,
                 stats,
                 rabbit_host,
                 rabbit_port,
                 rabbit_username,
                 rabbit_password,
                 rabbit_exchange,
                 rabbit_publish_key):

        self.url = url
        self.username = username
        self.password = password

        self.collection_id = None
        self.spider = None
        self.stats = stats

        self.rabbit_enabled = False
        if rabbit_host:
            self.rabbit_enabled = True
            self.rabbit_exchange = rabbit_exchange
            self.rabbit_publish_key = rabbit_publish_key

            self.channel = self._get_rabbit_channel(rabbit_host,
                                                    rabbit_port,
                                                    rabbit_username,
                                                    rabbit_password,
                                                    rabbit_exchange)

    @classmethod
    def from_crawler(cls, crawler):
        url = crawler.settings['KINGFISHER_API2_URL']
        username = crawler.settings['KINGFISHER_API2_USERNAME']
        password = crawler.settings['KINGFISHER_API2_PASSWORD']

        rabbit_host = crawler.settings['RABBIT_HOST']
        rabbit_port = crawler.settings['RABBIT_PORT']
        rabbit_username = crawler.settings['RABBIT_USERNAME']
        rabbit_password = crawler.settings['RABBIT_PASSWORD']
        rabbit_exchange = crawler.settings['RABBIT_EXCHANGE_NAME']
        rabbit_publish_key = crawler.settings['RABBIT_PUBLISH_KEY']

        stats = crawler.stats
        stats.set_value(KingfisherProcessAPI2.ITEMS_SENT_KEY_POST, 0)
        stats.set_value(KingfisherProcessAPI2.ITEMS_FAILED_KEY_POST, 0)
        stats.set_value(KingfisherProcessAPI2.ITEMS_SENT_KEY_RABBIT, 0)
        stats.set_value(KingfisherProcessAPI2.ITEMS_FAILED_KEY_RABBIT, 0)

        if not url:
            raise NotConfigured('KINGFISHER_API2_URL is not set.')

        if (username and not password) or (password and not username):
            raise NotConfigured('Both KINGFISHER_API2_USERNAME and KINGFISHER_API2_PASSWORD must be set.')

        extension = cls(url,
                        username,
                        password,
                        stats,
                        rabbit_host,
                        rabbit_port,
                        rabbit_username,
                        rabbit_password,
                        rabbit_exchange,
                        rabbit_publish_key)

        crawler.signals.connect(extension.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(extension.spider_closed, signal=signals.spider_closed)

        return extension

    def spider_opened(self, spider):
        """
        Sends an API request to start the collection in Kingfisher Process.
        """
        self.spider = spider

        data = {
            "source_id": spider.name,
            "data_version": spider.get_start_time('%Y-%m-%d %H:%M:%S'),
            "note": spider.note,
            "sample": spider.sample,
            "compile": True,
            "upgrade": spider.ocds_version == '1.0',
            "check": True,
        }

        response = self._post_sync("api/v1/create_collection", data)

        if not response.ok:
            spider.logger.warning(
                'Failed to POST create_collection. API status code: {}'.format(response.status_code))
        else:
            response_data = response.json()
            self.collection_id = response_data["collection_id"]
            spider.logger.info("Created collection in Kingfisher process with id {}".format(self.collection_id))

    def spider_closed(self, spider, reason):
        """
        Sends an API request to close the collection.
        """
        if not self.collection_id:
            # something went wrong in create collection file
            spider.logger.warning("No files were sent over to Kingfisher Process. Integration failed.")
            return

        # https://docs.scrapy.org/en/latest/topics/signals.html#spider-closed
        if spider.pluck or spider.keep_collection_open:
            return

        data = {
            "collection_id": self.collection_id,
            "reason": reason,
            "stats": json.loads(json.dumps(self.stats.get_stats(), default=str))
        }

        response = self._post_sync("api/v1/close_collection", data)
        if not response.ok:
            spider.logger.warning(
                "Failed to post close collection. API status code: {}".format(response.status_code))
        else:
            spider.logger.info("Closed collection in Kingfisher process with id {}".format(self.collection_id))

    def item_scraped(self, item, spider):
        """
        Sends an API request to store the file in Kingfisher Process.
        """
        if not self.collection_id:
            # probably create collection failed, skip
            return

        if isinstance(item, PluckedItem):
            return

        data = {
            "collection_id": self.collection_id,
            "path": os.path.join(item.get("files_store", ""), item.get("path", "")),
            "url": item.get("url", None)
        }

        if isinstance(item, FileError):
            # in case of error send info about it to api
            data["errors"] = json.dumps(item.get("errors", None))

        if self.rabbit_enabled:
            try:
                self._publish_to_rabbit(data)
                self.stats.inc_value(KingfisherProcessAPI2.ITEMS_SENT_KEY_RABBIT)
            except Exception as e:
                self.stats.inc_value(KingfisherProcessAPI2.ITEMS_FAILED_KEY_RABBIT)
                spider.logger.error("Unable to publish message to Rabbit %s", e)
        else:
            response = self._post_sync("api/v1/create_collection_file", data)
            if not response.ok:
                self.stats.inc_value(KingfisherProcessAPI2.ITEMS_FAILED_KEY_POST)
                spider.logger.warning("Failed to POST create_collection_file. API status code: {}".format(
                    response.status_code))
            else:
                self.stats.inc_value(KingfisherProcessAPI2.ITEMS_SENT_KEY_POST)
                spider.logger.debug("Sent POST to create collection file.")

    def _post_sync(self, url, data):
        """
        Posts synchronous requests to Kingfisher Process' API, adding authentication if needed.
        """
        kwargs = {}
        if self.username and self.password:
            kwargs['auth'] = (self.username, self.password)

        self.spider.logger.debug("Sent sync request to kingfisher process url {}/{} with data {}".format(
            self.url, url, data))
        return requests.post("{}/{}".format(self.url, url), json=data, **kwargs)

    def _publish_to_rabbit(self, message):
        self.channel.basic_publish(
            exchange=self.rabbit_exchange,
            routing_key=self.rabbit_publish_key,
            body=json.dumps(message),
            properties=BasicProperties(delivery_mode=2),
        )

    def _get_rabbit_channel(self,
                            rabbit_host,
                            rabbit_port,
                            rabbit_username,
                            rabbit_password,
                            rabbit_exchange):

        # connect to messaging
        credentials = PlainCredentials(rabbit_username, rabbit_password)

        connection = BlockingConnection(
            ConnectionParameters(
                host=rabbit_host,
                port=rabbit_port,
                credentials=credentials,
                blocked_connection_timeout=1800,
                heartbeat=0,
            )
        )

        rabbit_channel = connection.channel()

        # declare durable exchange
        rabbit_channel.exchange_declare(exchange=rabbit_exchange, durable="true", exchange_type="direct")

        return rabbit_channel
