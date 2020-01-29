import datetime
import json
import os

import requests
import scrapy


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
        Writes a ``kingfisher.collectioninfo`` metadata file in the crawl's directory.
        """
        data = {
            'source': self.name,
            'data_version': self._get_start_time(),
            'sample': self.is_sample(),
        }
        if hasattr(spider, 'note') and spider.note:
            data['note'] = spider.note

        self._write_file('kingfisher.collectioninfo', data)

    def spider_closed(self, spider, reason):
        """
        Writes a ``kingfisher-finished.collectioninfo`` metadata file in the crawl's directory.

        If the ``KINGFISHER_API_URI`` and ``KINGFISHER_API_KEY`` settings are set, sends a request to the Kingfisher
        Process service, to indicate that the collection is ended.
        """
        if reason != 'finished':
            return

        self._write_file('kingfisher-finished.collectioninfo', {
            'at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })

        settings = self.crawler.settings
        if settings['KINGFISHER_API_URI'] and settings['KINGFISHER_API_KEY']:
            response = requests.post(
                settings['KINGFISHER_API_URI'] + '/api/v1/submit/end_collection_store/',
                headers={
                    'Authorization': 'ApiKey ' + settings['KINGFISHER_API_KEY'],
                },
                data={
                    'collection_source': self.name,
                    'collection_data_version': self._get_start_time('%Y-%m-%d %H:%M:%S'),
                    'collection_sample': self.is_sample(),
                },
            )

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
        return os.path.join(name, self._get_start_time())

    def _get_start_time(self, format='%Y%m%d_%H%M%S'):
        return self.crawler.stats.get_value('start_time').strftime(format)


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
