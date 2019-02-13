import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class MoldovaRecords(BaseSpider):
    name = 'moldova_records'
    start_urls = ['http://ocds.mepps.openprocurement.io/api/records.json']

    def parse(self, response):
        json_data = json.loads(response.body_as_unicode())
        if not self.is_sample():
            if 'links' in json_data and 'next' in json_data['links']:
                yield scrapy.Request(json_data['links']['next'])

        yield {
            'file_urls': [response.url],
            'data_type': 'record_package'
        }
