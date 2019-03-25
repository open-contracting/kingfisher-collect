# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import hashlib
import json
import os
from zipfile import ZipFile

import requests
from scrapy.exceptions import DropItem, NotConfigured
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.python import to_bytes, to_native_str


class OldKingfisherFilesPipeline(FilesPipeline):

    @staticmethod
    def _get_start_time(spider):
        stats = spider.crawler.stats.get_stats()
        start_time = stats.get('start_time')
        return start_time

    def file_path(self, request, response=None, info=None):
        start_time = self._get_start_time(info.spider)
        start_time_str = start_time.strftime('%Y%m%d_%H%M%S')
        content_type = ''
        if response:
            # This is to cover the case when the url has . after the last /
            # and the text after the . is not a file extension but the response is a json
            content_type = to_native_str(response.headers['Content-Type'])
        url = request.url
        media_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        media_ext = os.path.splitext(url)[1]

        if hasattr(info.spider, 'ext'):
            media_ext = info.spider.ext
        elif not media_ext or ('json' in content_type and media_ext != '.json'):
            media_ext = '.json'
        # Put files in a directory named after the scraper they came from, and the scraper starttime
        if hasattr(info.spider, 'sample') and info.spider.sample == 'true':
            return '%s_sample/%s/%s%s' % (info.spider.name, start_time_str, media_guid, media_ext)
        else:
            return '%s/%s/%s%s' % (info.spider.name, start_time_str, media_guid, media_ext)

    def item_completed(self, results, item, info):

        """
        This is triggered when a JSON file has finished downloading.
        """

        if hasattr(info.spider, 'sample') and info.spider.sample == 'true':
            is_sample = True
        else:
            is_sample = False

        files_store = info.spider.crawler.settings.get('FILES_STORE')

        completed_files = []

        for ok, file_data in results:
            start_time = self._get_start_time(info.spider)
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
            if ok:
                file_url = file_data.get('url')
                local_path = os.path.join(files_store, file_data.get('path'))
                data_type = item.get('data_type')

                item_data = {
                    'success': True,
                    'collection_source': info.spider.name,
                    'collection_data_version': start_time_str,
                    'collection_sample': is_sample,
                    'file_name': local_path,
                    'url': file_url,
                    'data_type': data_type,
                    'local_path_inside_files_store': file_data.get('path'),
                    'local_path': local_path,
                }

                completed_files.append(item_data)
            else:

                # Currently, we only ever return 1 URL per item so we can assume zero here.
                url = item.get('file_urls')[0]

                item_data = {
                    'success': False,
                    'collection_source': info.spider.name,
                    'collection_data_version': start_time_str,
                    'collection_sample': is_sample,
                    'file_name': hashlib.sha1(to_bytes(url)).hexdigest()+'.json',
                    'url': url,
                    'error_message': str(file_data)
                }

                completed_files.append(item_data)

        return completed_files


class OldKingfisherPostPipeline(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self.api_url, self.api_headers, self.api_local_directory = self._build_api_info(crawler)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    @staticmethod
    def _get_start_time(spider):
        stats = spider.crawler.stats.get_stats()
        start_time = stats.get('start_time')
        return start_time

    @staticmethod
    def _build_api_info(crawler):
        api_uri = crawler.settings['KINGFISHER_API_URI']
        api_key = crawler.settings['KINGFISHER_API_KEY']
        api_local_directory = crawler.settings['KINGFISHER_API_LOCAL_DIRECTORY']

        if api_uri is None or api_key is None:
            raise NotConfigured('Kingfisher API not configured.')

        # TODO: figure out which api endpoint based on the data_type OR probably metadata passed from the spider

        headers = {'Authorization': 'ApiKey ' + api_key}
        return api_uri, headers, api_local_directory

    def process_item(self, item, spider):
        if hasattr(spider, 'sample') and spider.sample == 'true':
            is_sample = True
        else:
            is_sample = False
        data_version = self._get_start_time(spider).strftime('%Y-%m-%d %H:%M:%S')
        for completed in item:

            if completed['success']:

                data = {
                    'collection_source': spider.name,
                    'collection_data_version': data_version,
                    'collection_sample': is_sample,
                    'file_name': completed['file_name'],
                    'url': completed['url'],
                    'data_type': completed['data_type'],
                    'encoding': item['encoding']
                }

                if hasattr(spider, 'note') and spider.note:
                    data['collection_note'] = spider.note

                files = {}

                zipfile = None
                if hasattr(spider, 'ext') and spider.ext == '.zip':
                    zipfile = ZipFile(completed['local_path'])

                    files = {
                        'file': (completed['file_name'], zipfile.open(zipfile.namelist()[0]), 'application/json')
                    }
                else:
                    if self.api_local_directory:

                        full_local_filename = os.path.join(self.api_local_directory,
                                                           completed['local_path_inside_files_store'])
                        # At this point, we could test if the file path exists locally.
                        # But we aren't going to: it's possible the file path is different on the machine running scrape
                        # and the machine running process. (eg a network share mounted in different dirs)
                        data['local_file_name'] = full_local_filename

                    else:
                        files = {
                            'file': (completed['file_name'], open(completed['local_path'], 'rb'), 'application/json')
                        }

                response = requests.post(self.api_url + '/api/v1/submit/file/',
                                         data=data,
                                         files=files,
                                         headers=self.api_headers)

                if response.ok:
                    raise DropItem('Response from [{}] posted to API.'.format(completed.get('url')))
                else:
                    spider.logger.warning(
                        'Failed to post [{}]. API status code: {}'.format(completed.get('url'), response.status_code))
                if zipfile is not None:
                    zipfile.close()

            else:

                data = {
                    'collection_source': spider.name,
                    'collection_data_version': data_version,
                    'collection_sample': is_sample,
                    'file_name': completed['file_name'],
                    'url': completed['url'],
                    'errors': json.dumps([completed['error_message']]),
                }

                response = requests.post(self.api_url + '/api/v1/submit/file_errors/',
                                         data=data,
                                         headers=self.api_headers)
                if response.ok:
                    raise DropItem('Response from [{}] posted to File Errors API.'.format(completed.get('url')))
                else:
                    spider.logger.warning(
                        'Failed to post [{}]. File Errors API status code: {}'.format(completed.get('url'), response.status_code))


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

            data = {
                'collection_source': spider.name,
                'collection_data_version': self._get_start_time(spider).strftime('%Y-%m-%d %H:%M:%S'),
                'collection_sample': spider.is_sample(),
                'file_name': item['file_name'],
                'url': item['url'],
                'data_type': item['data_type'],
                # TODO add encoding
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
                    'file': (item['file_name'], open(spider.get_local_file_path_including_filestore(item['file_name']), 'rb'), 'application/json')
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

        else:

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
