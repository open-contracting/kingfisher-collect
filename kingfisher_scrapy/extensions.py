# https://docs.scrapy.org/en/latest/topics/extensions.html#writing-your-own-extension

import json
import os

import requests
import sentry_sdk
from scrapy import signals
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.items import File, FileError, FileItem, PluckedItem
from kingfisher_scrapy.kingfisher_process import Client
from kingfisher_scrapy.util import _pluck_filename


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

        self._write(spider, reason)

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
        If the item is a file, writes its data to the filename in the crawl's directory.

        Returns a dict with the metadata.
        """
        if not isinstance(item, File):
            return

        # The crawl's relative directory, in the format `<spider_name>[_sample]/<YYMMDD_HHMMSS>`.
        name = spider.name
        if spider.sample:
            name += '_sample'
        path = os.path.join(name, spider.get_start_time('%Y%m%d_%H%M%S'), item['file_name'])

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
                json.dump(data, f)


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
        if reason != 'finished' or spider.pluck or spider.keep_collection_open:
            return

        response = self.client.end_collection_store({
            'collection_source': spider.name,
            'collection_data_version': spider.get_start_time('%Y-%m-%d %H:%M:%S'),
            'collection_sample': spider.sample,
        })

        if not response.ok:
            spider.logger.warning(
                'Failed to post End Collection Store. API status code: {}'.format(response.status_code))

    def item_scraped(self, item, spider):
        """
        Sends an API request to store the file, file item or file error in Kingfisher Process.
        """

        if not item.get('post_to_api', True) or isinstance(item, PluckedItem):
            return

        data = {
            'collection_source': spider.name,
            'collection_data_version': spider.get_start_time('%Y-%m-%d %H:%M:%S'),
            'collection_sample': spider.sample,
            'file_name': item['file_name'],
            'url': item['url'],
        }

        if isinstance(item, FileError):
            data['errors'] = json.dumps(item['errors'])

            self._request(item, spider, 'create_file_error', data, name='File Errors API')
        else:
            data['data_type'] = item['data_type']
            data['encoding'] = item.get('encoding', 'utf-8')
            if spider.note:
                data['collection_note'] = spider.note

            if isinstance(item, FileItem):
                data['number'] = item['number']
                data['data'] = item['data']

                self._request(item, spider, 'create_file_item', data)

            # File
            else:
                if self.directory:
                    path = item['path']
                    data['local_file_name'] = os.path.join(self.directory, path)
                    files = {}
                else:
                    path = os.path.join(item['files_store'], item['path'])
                    f = open(path, 'rb')
                    files = {'file': (item['file_name'], f, 'application/json')}

                self._request(item, spider, 'create_file', data, files)

    def _request(self, item, spider, method, *args, name='API'):
        response = getattr(self.client, method)(*args)
        if not response.ok:
            spider.logger.warning(
                'Failed to post [{}]. {} status code: {}'.format(item['url'], name, response.status_code))


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


class KingfisherProcessNGAPI:
    """
    If the ``KINGFISHER_API_URI`` and ``KINGFISHER_API_KEY`` environment variables or configuration settings are set,
    then messages are sent to a Kingfisher Process API for the ``item_scraped`` and ``spider_closed`` signals.
    """
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    @classmethod
    def from_crawler(cls, crawler):
        url = crawler.settings['KINGFISHER_NG_API_URI']
        username = crawler.settings['KINGFISHER_NG_API_USERNAME']
        password = crawler.settings['KINGFISHER_NG_API_PASSWORD']

        if not url:
            raise NotConfigured('KINGFISHER_NG_API_URI is not set.')

        extension = cls(url, username, password)
        crawler.signals.connect(extension.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(extension.spider_closed, signal=signals.spider_closed)

        return extension

    def spider_opened(self, spider):
        """
        Sends an API request to start the collection in KP.
        """
        data = {
            "source_id": spider.name,
            "data_version": spider.get_start_time('%Y-%m-%d %H:%M:%S'),
            "note": "collected by scrapy",
            "sample": spider.sample,
            "compile": True,
            "upgrade": True,
            "check": True,
        }

        response = self._post("api/v1/create_collection", data)

        if not response.ok:
            spider.logger.warning(
                'Failed to POST create_collection. API status code: {}'.format(response.status_code))
        else:
            response_data = json.loads(response.text)
            self.collection_id = response_data["collection_id"]

    def spider_closed(self, spider, reason):
        """
        Sends an API request to close the collection.
        """
        if reason != 'finished' or spider.pluck or spider.keep_collection_open:
            return

        data = {
            "collection_id": self.collection_id,
        }

        response = self._post("api/v1/close_collection", data)


        if not response.ok:
            spider.logger.warning(
                'Failed to post close collection. API status code: {}'.format(response.status_code))


    def item_scraped(self, item, spider):
        """
        Sends an API request to store the file in Kingfisher Process.
        """
        data = {
            "collection_id": self.collection_id,
            "path": os.path.join(item['files_store'], item['path'])
        }

        response = self._post("api/v1/create_collection_file", data)

        if not response.ok:
            spider.logger.warning(
                'Failed to POST create_collection_file. API status code: {}'.format(response.status_code))

    def _post(self, url, data):
        """
        Wrapper around the requests.
        """
        if self.username and self.password:
            return requests.post("{}/{}".format(self.url, url), json=data, auth=(self.username, self.password))
        else:
            return requests.post("{}/{}".format(self.url, url), json=data)
