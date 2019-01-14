# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json
import hashlib
import requests

from scrapy.pipelines.files import FilesPipeline, GCSFilesStore
from scrapy.utils.python import to_bytes
from scrapy.exceptions import DropItem, NotConfigured


class KingfisherFilesPipeline(FilesPipeline):

    def _get_start_time(self, spider):
        stats = spider.crawler.stats.get_stats()
        start_time = stats.get("start_time")
        return start_time

    def file_path(self, request, response=None, info=None):
        start_time = self._get_start_time(info.spider)
        start_time_str = start_time.strftime("%Y%m%d_%H%M%S")

        url = request.url
        media_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        media_ext = os.path.splitext(url)[1]

        if not media_ext:
            media_ext = '.json'
        # Put files in a directory named after the scraper they came from, and the scraper starttime
        return '%s/%s/%s%s' % (info.spider.name, start_time_str, media_guid, media_ext)

    def item_completed(self, results, item, info):

        """
        This is triggered when a JSON file has finished downloading.
        """

        if hasattr(info.spider, 'sample')  and info.spider.sample == 'true':
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
                    "data": json_from_file
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

    def _build_api_url(self, crawler):
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
        for completed in item:

            headers['Content-Type'] = 'application/json'
            
            response = requests.post(url, json=completed, headers=headers)
            if response.ok:
                raise DropItem("Response from [{}] posted to API.".format(completed.get('url')))
            else:
                spider.logger.warning("Failed to post [{}]. API status code: {}".format(completed.get('url'), response.status_code))


class GCSFilesStoreJSON(GCSFilesStore):
    CREDENTIALS = {
        "type": "service_account",
        "project_id": os.environ.get("GCS_PROJECT_ID"),
        "private_key_id": os.environ.get("GCS_PRIVATE_KEY_ID"),
        "private_key": os.environ.get("GCS_PRIVATE_KEY"),
        "client_email": os.environ.get("GCS_CLIENT_EMAIL"),
        "client_id": os.environ.get("GCS_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get("GCS_CLIENT_X509_CERT_URL")
    }

    def __init__(self, uri):
        from google.cloud import storage
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_info(self.CREDENTIALS)
        client = storage.Client(credentials=credentials)
        bucket, prefix = uri[5:].split('/', 1)
        self.bucket = client.bucket(bucket)
        self.prefix = prefix


class GCSFilePipeline(FilesPipeline):
    def __init__(self, store_uri, download_func=None, settings=None):
        super(GCSFilePipeline, self).__init__(store_uri, download_func, settings)
