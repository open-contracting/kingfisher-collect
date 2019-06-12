import os
import datetime

import requests
import scrapy
import json

# This file contain base spiders all our spiders extend from, so we can add some custom functionality
#
# However, we need to do this for several base spiders. To avoid copying and pasting code between base spiders,
#  some code is put into generic functions


def _generic_get_start_time(called_on_class):
    stats = called_on_class.crawler.stats.get_stats()
    start_time = stats.get("start_time")
    return start_time


def _generic_is_sample(called_on_class):
    return hasattr(called_on_class, 'sample') and called_on_class.sample == 'true'


def _dump_information_file(called_on_class, spider, filename, data):
    source_name_with_sample = called_on_class.name + ('_sample' if called_on_class.is_sample() else '')
    directory = os.path.join(
        called_on_class.crawler.settings['FILES_STORE'],
        source_name_with_sample,
        called_on_class._get_start_time().strftime("%Y%m%d_%H%M%S"),
    )
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(os.path.join(directory, filename), 'w') as f:
        f.write(json.dumps(data))


def _generic_spider_opened(called_on_class, spider):
    data = {
        'source': called_on_class.name,
        'data_version': called_on_class._get_start_time().strftime("%Y%m%d_%H%M%S"),
        'sample': called_on_class.is_sample(),
    }
    if hasattr(spider, 'note') and spider.note:
        data['note'] = spider.note
    _dump_information_file(called_on_class, spider, 'kingfisher.collectioninfo', data)


def _generic_spider_closed(called_on_class, spider, reason):
    if reason == 'finished' \
            and called_on_class.crawler.settings['KINGFISHER_API_URI'] \
            and called_on_class.crawler.settings['KINGFISHER_API_KEY']:

        headers = {"Authorization": "ApiKey " + called_on_class.crawler.settings['KINGFISHER_API_KEY']}
        data = {
            "collection_source": called_on_class.name,
            "collection_data_version": called_on_class._get_start_time().strftime("%Y-%m-%d %H:%M:%S"),
            "collection_sample": called_on_class.is_sample(),
        }

        response = requests.post(
            called_on_class.crawler.settings['KINGFISHER_API_URI'] + '/api/v1/submit/end_collection_store/',
            data=data,
            headers=headers)

        if not response.ok:
            spider.logger.warning(
                "Failed to post End Collection Store. API status code: {}".format(response.status_code))

    if reason == 'finished':
        _dump_information_file(
            called_on_class,
            spider,
            'kingfisher-finished.collectioninfo',
            {'at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        )


def _generic_get_local_file_path_excluding_filestore(called_on_class, filename):
    source_name_with_sample = called_on_class.name + ('_sample' if called_on_class.is_sample() else '')
    return os.path.join(
        source_name_with_sample,
        called_on_class._get_start_time().strftime("%Y%m%d_%H%M%S"),
        filename
    )


def _generic_get_local_file_path_including_filestore(called_on_class, filename):
    source_name_with_sample = called_on_class.name + ('_sample' if called_on_class.is_sample() else '')
    return os.path.join(
        called_on_class.crawler.settings['FILES_STORE'],
        source_name_with_sample,
        called_on_class._get_start_time().strftime("%Y%m%d_%H%M%S"),
        filename
    )


def _generic_scrapy_save_response_to_disk(called_on_class, response, filename, is_response=True, data_type=None, encoding='utf8'):

    source_name_with_sample = called_on_class.name + ('_sample' if called_on_class.is_sample() else '')
    directory = os.path.join(
        called_on_class.crawler.settings['FILES_STORE'],
        source_name_with_sample,
        called_on_class._get_start_time().strftime("%Y%m%d_%H%M%S"),
    )
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(os.path.join(directory, filename), 'wb') as f:
        if is_response:
            f.write(response.body)
        else:
            f.write(response)

    with open(os.path.join(directory, filename + '.fileinfo'), 'w') as f:
        f.write(json.dumps({
            'url': response.request.url,
            'data_type': data_type,
            'encoding': encoding,
        }))

    return {
        'success': True,
        'file_name': filename,
        "data_type": data_type,
        "url": response.request.url,
        'encoding': encoding,
    }

# Now we have our own base spiders (that use our generic functions)


class BaseSpider(scrapy.Spider):

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def _get_start_time(self):
        return _generic_get_start_time(called_on_class=self)

    def is_sample(self):
        return _generic_is_sample(called_on_class=self)

    def spider_opened(self, spider):
        return _generic_spider_opened(self, spider)

    def spider_closed(self, spider, reason):
        return _generic_spider_closed(self, spider, reason)

    def get_local_file_path_including_filestore(self, filename):
        return _generic_get_local_file_path_including_filestore(self, filename)

    def get_local_file_path_excluding_filestore(self, filename):
        return _generic_get_local_file_path_excluding_filestore(self, filename)

    def save_response_to_disk(self, response, filename, is_response=True, data_type=None, encoding='utf-8'):
        return _generic_scrapy_save_response_to_disk(self, response, filename, is_response=is_response, data_type=data_type, encoding=encoding)


class BaseXMLFeedSpider(scrapy.spiders.XMLFeedSpider):

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BaseXMLFeedSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=scrapy.signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=scrapy.signals.spider_closed)
        return spider

    def _get_start_time(self):
        return _generic_get_start_time(called_on_class=self)

    def is_sample(self):
        return _generic_is_sample(called_on_class=self)

    def spider_opened(self, spider):
        return _generic_spider_opened(self, spider)

    def spider_closed(self, spider, reason):
        return _generic_spider_closed(self, spider, reason)

    def get_local_file_path_including_filestore(self, filename):
        return _generic_get_local_file_path_including_filestore(self, filename)

    def get_local_file_path_excluding_filestore(self, filename):
        return _generic_get_local_file_path_excluding_filestore(self, filename)

    def save_response_to_disk(self, response, filename, is_response=True, data_type=None, encoding='utf-8'):
        return _generic_scrapy_save_response_to_disk(self, response, filename, is_response=is_response, data_type=data_type, encoding=encoding)
