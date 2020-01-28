# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os

import requests
from scrapy.exceptions import DropItem, NotConfigured


class KingfisherPostPipeline(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self._build_api_info(crawler)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    @staticmethod
    def _get_start_time(spider):
        stats = spider.crawler.stats.get_stats()
        start_time = stats.get('start_time')
        return start_time

    def _build_api_info(self, crawler):
        self.api_url = crawler.settings['KINGFISHER_API_URI']
        api_key = crawler.settings['KINGFISHER_API_KEY']
        self.api_local_directory = crawler.settings['KINGFISHER_API_LOCAL_DIRECTORY']

        if self.api_url is None or api_key is None:
            raise NotConfigured('Kingfisher API not configured.')

        self.api_headers = {'Authorization': 'ApiKey ' + api_key}

    def process_item(self, item, spider):

        if item['success']:
            if 'number' in item and item['number']:
                self._process_item_success(item, spider)
            else:
                self._process_file_success(item, spider)
        else:
            self._process_failure(item, spider)

    def _process_item_success(self, item, spider):
        """
        Process a data item from Scrapy, that should be passed to the API as an Item via /api/v1/submit/item/!

        (Commenting to make sure people note the confusing fact that "item" has 2 meanings here!)
        """

        data = {
            'collection_source': spider.name,
            'collection_data_version': self._get_start_time(spider).strftime('%Y-%m-%d %H:%M:%S'),
            'collection_sample': spider.is_sample(),
            'file_name': item['file_name'],
            'url': item['url'],
            'data_type': item['data_type'],
            'number': item['number'],
            'data': item['data'],
            'encoding': item.get('encoding', 'utf-8'),
        }

        if hasattr(spider, 'note') and spider.note:
            data['collection_note'] = spider.note

        response = requests.post(self.api_url + '/api/v1/submit/item/',
                                 data=data,
                                 headers=self.api_headers)

        if response.ok:
            raise DropItem('Response from [{}] posted to API.'.format(item['url']))
        else:
            spider.logger.warning(
                'Failed to post [{}]. API status code: {}'.format(item['url'], response.status_code))

    def _process_file_success(self, item, spider):
        """
        Process a data item from Scrapy, that should be passed to the API as a file via /api/v1/submit/file/!

        (Commenting to make sure people note the confusing fact that "item" has 2 meanings here!)
        """

        data = {
            'collection_source': spider.name,
            'collection_data_version': self._get_start_time(spider).strftime('%Y-%m-%d %H:%M:%S'),
            'collection_sample': spider.is_sample(),
            'file_name': item['file_name'],
            'url': item['url'],
            'data_type': item['data_type'],
            'encoding': item.get('encoding', 'utf-8'),
        }

        if hasattr(spider, 'note') and spider.note:
            data['collection_note'] = spider.note

        files = {}

        if self.api_local_directory:

            full_local_filename = os.path.join(self.api_local_directory,
                                               spider.get_local_file_path_excluding_filestore(item['file_name']))
            # At this point, we could test if the file path exists locally.
            # But we aren't going to: it's possible the file path is different on the machine running scrape
            # and the machine running process. (eg a network share mounted in different dirs)
            data['local_file_name'] = full_local_filename

        else:
            files = {
                'file': (
                    item['file_name'], open(spider.get_local_file_path_including_filestore(item['file_name']), 'rb'),
                    'application/json'
                )
            }

        response = requests.post(self.api_url + '/api/v1/submit/file/',
                                 data=data,
                                 files=files,
                                 headers=self.api_headers)

        if response.ok:
            raise DropItem('Response from [{}] posted to API.'.format(item['url']))
        else:
            spider.logger.warning(
                'Failed to post [{}]. API status code: {}'.format(item['url'], response.status_code))

    def _process_failure(self, item, spider):

        data = {
            'collection_source': spider.name,
            'collection_data_version': self._get_start_time(spider).strftime('%Y-%m-%d %H:%M:%S'),
            'collection_sample': spider.is_sample(),
            'file_name': item['file_name'],
            'url': item['url'],
            'errors': json.dumps(item['errors']),
        }

        response = requests.post(self.api_url + '/api/v1/submit/file_errors/',
                                 data=data,
                                 headers=self.api_headers)
        if response.ok:
            raise DropItem('Response from [{}] posted to File Errors API.'.format(item['url']))
        else:
            spider.logger.warning(
                'Failed to post [{}]. File Errors API status code: {}'.format(item['url'],
                                                                              response.status_code))
