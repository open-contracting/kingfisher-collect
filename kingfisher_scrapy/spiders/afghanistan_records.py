import json

import scrapy


class AfghanistanRecords(scrapy.Spider):
    name = 'afghanistan_records'
    start_urls = ['https://ocds.ageops.net/api/ocds/records']

    def parse(self, response):
        files_urls = json.loads(response.body)
        if hasattr(self, 'sample') and self.sample == 'true':
            files_urls = [files_urls[0]]

        yield {
            'file_urls': files_urls,
            'data_type': 'record'
        }
