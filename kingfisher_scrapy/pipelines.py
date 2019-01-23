# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import hashlib
import requests
import tarfile
from zipfile import ZipFile

from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.python import to_bytes, to_native_str
from scrapy.exceptions import DropItem, NotConfigured


class KingfisherFilesPipeline(FilesPipeline):
    
    def _get_file_contents(self, path, ext = '.zip'):
        # TODO scan the zip file for more than one file?
        if ext == '.zip':
            with ZipFile(path) as zipfile:
                with zipfile.open(zipfile.namelist()[0]) as plainfile:
                    return json.loads(plainfile.read())
        elif ext == '.tar.gz':
            with tarfile.open(path,'r:gz') as tarfile:
                f = tarfile.extractfile(tarfile.getmembers()[0])
                return json.loads(f.read())
        raise RuntimeError('Undefined file extension: ' + ext)

    @staticmethod
    def _get_start_time(self, spider):
        stats = spider.crawler.stats.get_stats()
        start_time = stats.get("start_time")
        return start_time

    def file_path(self, request, response=None, info=None):
        start_time = self._get_start_time(info.spider)
        start_time_str = start_time.strftime("%Y%m%d_%H%M%S")
        content_type = ''
        if response:
            # This is to cover the case when the url has . after the last /
            # and the text after the . is not a file extension but the response is a json
            content_type = to_native_str(response.headers['Content-Type'])
        url = request.url
        media_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        media_ext = os.path.splitext(url)[1]

        if hasattr(info.spider,'ext'):
            media_ext = info.spider.ext
        elif not media_ext or ('json' in content_type and media_ext != '.json'):
            media_ext = '.json'
        # Put files in a directory named after the scraper they came from, and the scraper starttime
        return '%s/%s/%s%s' % (info.spider.name, start_time_str, media_guid, media_ext)

    def item_completed(self, results, item, info):

        """
        This is triggered when a JSON file has finished downloading.
        """

        if hasattr(info.spider, 'sample') and info.spider.sample == 'true':
            is_sample = True
        else:
            is_sample = False

        files_store = info.spider.crawler.settings.get("FILES_STORE")

        completed_files = []

        for ok, file_data in results:
            if ok:
                file_url = file_data.get("url")
                local_path = os.path.join(files_store, file_data.get("path"))
                start_time = self._get_start_time(info.spider)
                start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
                data_type = item.get("data_type")

                if hasattr(info.spider,'ext'):
                    json_from_file = self._get_file_contents(local_path, info.spider.ext)
                else:
                    with open(local_path) as json_file:
                        json_from_file = json.load(json_file)

                item_data = {
                    "collection_source": info.spider.name,
                    "collection_data_version": start_time_str,
                    "collection_sample": is_sample,
                    "file_name": local_path,
                    "url": file_url,
                    "data_type": data_type,
                    "local_path": local_path,
                }

                completed_files.append(item_data)

        return completed_files


class KingfisherPostPipeline(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self.api_url = self._build_api_url(crawler)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    @staticmethod
    def _get_start_time(spider):
        stats = spider.crawler.stats.get_stats()
        start_time = stats.get("start_time")
        return start_time

    @staticmethod
    def _build_api_url(crawler):
        api_uri = crawler.settings['KINGFISHER_API_FILE_URI']
        api_item_uri = crawler.settings['KINGFISHER_API_ITEM_URI']
        api_key = crawler.settings['KINGFISHER_API_KEY']

        if api_uri is None or api_item_uri is None or api_key is None:
            raise NotConfigured('Kingfisher API not configured.')

        # TODO: figure out which api endpoint based on the data_type OR probably metadata passed from the spider

        headers = {"Authorization": "ApiKey " + api_key}
        return api_uri, headers

    def process_item(self, item, spider):
        url, headers = self.api_url
        if hasattr(spider, 'sample') and spider.sample == 'true':
            is_sample = True
        else:
            is_sample = False
        data_version = self._get_start_time(spider).strftime("%Y-%m-%d %H:%M:%S")
        for completed in item:

            data = {
                "collection_source": spider.name,
                "collection_data_version": data_version,
                "collection_sample": is_sample,
                "file_name": completed['file_name'],
                "url": completed['url'],
                "data_type": completed['data_type'],
                # TODO add encoding
            }

            files = {
                'file': (completed['file_name'], open(completed['local_path'], 'rb'), 'application/json')
            }

            response = requests.post(url, data=data, files=files, headers=headers)
            if response.ok:
                raise DropItem("Response from [{}] posted to API.".format(completed.get('url')))
            else:
                spider.logger.warning(
                    "Failed to post [{}]. API status code: {}".format(completed.get('url'), response.status_code))
