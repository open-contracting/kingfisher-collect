import json
import os

from scrapy import signals
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.kingfisher_process import Client


# https://docs.scrapy.org/en/latest/topics/extensions.html#writing-your-own-extension
class KingfisherFilesStore:
    def __init__(self, directory):
        self.directory = directory

    @classmethod
    def from_crawler(cls, crawler):
        directory = crawler.settings['FILES_STORE']
        extension = cls(directory)
        crawler.signals.connect(extension.item_scraped, signal=signals.item_scraped)
        return extension

    def item_scraped(self, item, spider):
        """
        Writes the item's data to the filename in the crawl's directory.

        Writes a ``<filename>.fileinfo`` metadata file in the crawl's directory, and returns a dict with the metadata.
        """
        if item['success'] is False:
            return

        if 'number' not in item:
            self._write_file(item['file_name'], item['data'], spider)
            metadata = {
                'url': item['url'],
                'data_type': item['data_type'],
                'encoding': item['encoding'],
            }
            self._write_file(item['file_name'] + '.fileinfo', metadata, spider)
        item['path_including_file_store'] = self.get_local_file_path_including_filestore(item['file_name'],
                                                                                         spider)
        item['path_excluding_file_store'] = self.get_local_file_path_excluding_filestore(item['file_name'],
                                                                                         spider)

    def _write_file(self, filename, data, spider):
        path = self.get_local_file_path_including_filestore(filename, spider)
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

    def get_local_file_path_including_filestore(self, filename, spider):
        """
        Prepends Scrapy's storage directory and the crawl's relative directory to the filename.
        """
        return os.path.join(self.directory, self._get_crawl_path(spider), filename)

    def get_local_file_path_excluding_filestore(self, filename, spider):
        """
        Prepends the crawl's relative directory to the filename.
        """
        return os.path.join(self._get_crawl_path(spider), filename)

    def _get_crawl_path(self, spider):
        name = spider.name
        if spider.sample:
            name += '_sample'
        return os.path.join(name, spider.get_start_time('%Y%m%d_%H%M%S'))


class KingfisherAPI:
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
        if reason != 'finished':
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
        If the Scrapy item indicates success, sends a Kingfisher Process API request to create either a Kingfisher
        Process file or file item. Otherwise, sends an API request to create a file error.
        """
        if not item.get('post_to_api', True):
            return

        data = {
            'collection_source': spider.name,
            'collection_data_version': spider.get_start_time('%Y-%m-%d %H:%M:%S'),
            'collection_sample': spider.sample,
            'file_name': item['file_name'],
            'url': item['url'],
        }

        if item['success']:
            data['data_type'] = item['data_type']
            data['encoding'] = item.get('encoding', 'utf-8')
            if spider.note:
                data['collection_note'] = spider.note

            # File Item
            if 'number' in item:
                data['number'] = item['number']
                data['data'] = item['data']

                self._request(item, spider, 'create_file_item', data)

            # File
            else:
                if self.directory:
                    path = item['path_excluding_file_store']
                    data['local_file_name'] = os.path.join(self.directory, path)
                    files = {}
                else:
                    path = item['path_including_file_store']
                    f = open(path, 'rb')
                    files = {'file': (item['file_name'], f, 'application/json')}

                self._request(item, spider, 'create_file', data, files)

        # File Error
        else:
            data['errors'] = json.dumps(item['errors'])

            self._request(item, spider, 'create_file_error', data, name='File Errors API')

    def _request(self, item, spider, method, *args, name='API'):
        response = getattr(self.client, method)(*args)
        if not response.ok:
            spider.logger.warning(
                'Failed to post [{}]. {} status code: {}'.format(item['url'], name, response.status_code))
