# https://docs.scrapy.org/en/latest/topics/extensions.html#writing-your-own-extension

import json
import os

import sentry_sdk
from scrapy import signals
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy import util
from kingfisher_scrapy.items import File, FileError, FileItem, PluckedItem
from kingfisher_scrapy.kingfisher_process import Client
from kingfisher_scrapy.util import _pluck_filename, get_file_name_and_extension


# https://docs.scrapy.org/en/latest/topics/extensions.html#writing-your-own-extension
class KingfisherPluck:
    def __init__(self, directory):
        self.directory = directory
        self.spiders_seen = set()

    @classmethod
    def from_crawler(cls, crawler):
        directory = crawler.settings['KINGFISHER_PLUCK_PATH']

        extension = cls(directory=directory)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(extension.spider_closed, signal=signals.spider_closed)

        return extension

    def item_scraped(self, item, spider):
        if not spider.pluck or spider.name in self.spiders_seen or not isinstance(item, PluckedItem):
            return

        self.spiders_seen.add(spider.name)

        self._write(spider, item['value'])

    def spider_closed(self, spider, reason):
        if not spider.pluck or spider.name in self.spiders_seen:
            return

        self._write(spider, f'closed: {reason}')

    def _write(self, spider, value):
        with open(os.path.join(self.directory, _pluck_filename(spider)), 'a+') as f:
            f.write(f'{value},{spider.name}\n')


class KingfisherFilesStore:
    def __init__(self, directory):
        self.directory = directory

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

        # The crawl's relative directory, in the format `<spider_name>[_sample]/<YYMMDD_HHMMSS>`.
        folder_name = spider.name
        if spider.sample:
            folder_name += '_sample'

        file_name = item['file_name']
        if isinstance(item, FileItem):
            name, extension = get_file_name_and_extension(file_name)
            file_name = f"{name}-{item['number']}.{extension}"

        path = os.path.join(folder_name, spider.get_start_time('%Y%m%d_%H%M%S'), file_name)

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


class KingfisherItemCount:
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

        extension = cls(url, key, directory=directory)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(extension.spider_closed, signal=signals.spider_closed)

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
        data = self._build_data_to_send(spider, file_name, response.request.url, failure)
        return self._request(spider, 'create_file_error', response.request.url, data)

    def item_error(self, item, response, spider, failure):
        """
        Sends an API request to store a file error in Kingfisher Process when a item pipeline generates an error.
        """
        # https://docs.scrapy.org/en/latest/topics/signals.html#scrapy.signals.item_error
        data = self._build_data_to_send(spider, item['file_name'], item['url'], failure)
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
            data['data'] = item['data']

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
            'collection_sample': str(bool(spider.sample))
        }
        if file_name:
            data['file_name'] = file_name
        if url:
            data['url'] = url
        if errors:
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
