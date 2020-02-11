import datetime
import hashlib
import json
import os

import scrapy

from kingfisher_scrapy.kingfisher_process import Client


class KingfisherSpiderMixin:
    def is_sample(self):
        """
        Returns whether the ``sample`` spider argument was set to 'true'.

        .. code:: bash

           scrapy crawl spider_name -a sample=true
        """
        return hasattr(self, 'sample') and self.sample == 'true'

    def spider_opened(self, spider):
        """
        Writes a ``kingfisher.collectioninfo`` metadata file in the crawl's directory, and initializes a Kingfisher
        Process API client.
        """
        data = {
            'source': self.name,
            'data_version': self.get_start_time('%Y%m%d_%H%M%S'),
            'sample': self.is_sample(),
        }
        if hasattr(spider, 'note') and spider.note:
            data['note'] = spider.note

        self._write_file('kingfisher.collectioninfo', data)

        self.client = Client(self.crawler.settings['KINGFISHER_API_URI'], self.crawler.settings['KINGFISHER_API_KEY'])

    def spider_closed(self, spider, reason):
        """
        Writes a ``kingfisher-finished.collectioninfo`` metadata file in the crawl's directory. If the Kingfisher
        Process API client is configured, sends an API request to end the collection's store step.
        """
        if reason != 'finished':
            return

        self._write_file('kingfisher-finished.collectioninfo', {
            'at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })

        if self.client.configured:
            response = self.client.end_collection_store({
                'collection_source': self.name,
                'collection_data_version': self.get_start_time('%Y-%m-%d %H:%M:%S'),
                'collection_sample': self.is_sample(),
            })

            if not response.ok:
                spider.logger.warning(
                    'Failed to post End Collection Store. API status code: {}'.format(response.status_code))

    def get_local_file_path_including_filestore(self, filename):
        """
        Prepends Scrapy's storage directory and the crawl's relative directory to the filename.
        """
        return os.path.join(self.crawler.settings['FILES_STORE'], self._get_crawl_path(), filename)

    def get_local_file_path_excluding_filestore(self, filename):
        """
        Prepends the crawl's relative directory to the filename.
        """
        return os.path.join(self._get_crawl_path(), filename)

    def save_response_to_disk(self, response, filename, data_type=None, encoding='utf-8'):
        """
        Writes the response's body to the filename in the crawl's directory.

        Writes a ``<filename>.fileinfo`` metadata file in the crawl's directory, and returns a dict with the metadata.
        """
        return self._save_response_to_disk(response.body, filename, response.request.url, data_type, encoding)

    def save_data_to_disk(self, data, filename, url=None, data_type=None, encoding='utf-8'):
        """
        Writes the data to the filename in the crawl's directory.

        Writes a ``<filename>.fileinfo`` metadata file in the crawl's directory, and returns a dict with the metadata.
        """
        return self._save_response_to_disk(data, filename, url, data_type, encoding)

    def get_start_time(self, format):
        """
        Returns the formatted start time of the crawl.
        """
        return self.crawler.stats.get_value('start_time').strftime(format)

    def _save_response_to_disk(self, data, filename, url, data_type, encoding):
        self._write_file(filename, data)

        metadata = {
            'url': url,
            'data_type': data_type,
            'encoding': encoding,
        }

        self._write_file(filename + '.fileinfo', metadata)

        metadata['success'] = True
        metadata['file_name'] = filename

        return metadata

    def _write_file(self, filename, data):
        path = self.get_local_file_path_including_filestore(filename)
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

    def _get_crawl_path(self):
        name = self.name
        if self.is_sample():
            name += '_sample'
        return os.path.join(name, self.get_start_time('%Y%m%d_%H%M%S'))


class LinksSpider:
    @staticmethod
    def next_link(response):
        """
        Handling API response with a links field

        Access to ``links/next`` for the new url, and returns a Request
        """
        json_data = json.loads(response.text)
        if 'links' in json_data and 'next' in json_data['links']:
            url = json_data['links']['next']
            return scrapy.Request(
                url=url,
                meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
            )


class BaseSpider(scrapy.Spider, KingfisherSpiderMixin):
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider


class BaseXMLFeedSpider(scrapy.spiders.XMLFeedSpider, KingfisherSpiderMixin):
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseXMLFeedSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider
