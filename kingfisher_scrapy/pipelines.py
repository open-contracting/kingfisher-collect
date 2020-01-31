# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os

from scrapy.exceptions import DropItem, NotConfigured


class KingfisherPostPipeline:
    def __init__(self, url=None, key=None, directory=None):
        if url is None or key is None:
            raise NotConfigured('Kingfisher API not configured.')
        self.directory = directory

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            url=crawler.settings['KINGFISHER_API_URI'],
            key=crawler.settings['KINGFISHER_API_KEY'],
            directory=crawler.settings['KINGFISHER_API_LOCAL_DIRECTORY'],
        )

    def process_item(self, item, spider):
        """
        If the Scrapy item indicates success, sends a Kingfisher Process API request to create either a Kingfisher
        Process file or file item. Otherwise, sends an API request to create a file error.
        """
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
            if item.get('number'):
                data['number'] = item['number']
                data['data'] = item['data']

                self._post(item, spider, 'create_file_item', data)

            # File
            else:
                if self.directory:
                    path = spider.get_local_file_path_excluding_filestore(item['file_name'])
                    data['local_file_name'] = os.path.join(self.directory, path)
                    files = {}
                else:
                    path = spider.get_local_file_path_including_filestore(item['file_name'])
                    f = open(path, 'rb')
                    files = {'file': (item['file_name'], f, 'application/json')}

                self._post(item, spider, 'create_file', data, files)

        # File Error
        else:
            data['errors'] = json.dumps(item['errors'])

            self._post(item, spider, 'create_file_error', data, name='File Errors API')

    def _post(self, item, spider, method, *args, name='API'):
        response = getattr(spider.client, method)(*args)
        if response.ok:
            raise DropItem('Response from [{}] posted to {}.'.format(item['url'], name))
        else:
            spider.logger.warning(
                'Failed to post [{}]. {} status code: {}'.format(item['url'], name, response.status_code))
