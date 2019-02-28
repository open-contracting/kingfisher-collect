import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


# This Spider uses the old system of pipelines! DO NOT USE IT AS AN EXAMPLE OF WHAT TO DO IN FUTURE SPIDERS!
# Thank you.
class MoldovaRecords(BaseSpider):
    name = 'moldova_records'
    start_urls = ['http://ocds.mepps.openprocurement.io/api/records.json']
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.OldKingfisherFilesPipeline': 400,
            'kingfisher_scrapy.pipelines.OldKingfisherPostPipeline': 800,
        }
    }

    def parse(self, response):
        json_data = json.loads(response.body_as_unicode())
        if not self.is_sample():
            if 'links' in json_data and 'next' in json_data['links']:
                yield scrapy.Request(json_data['links']['next'])

        yield {
            'file_urls': [response.url],
            'data_type': 'record_package'
        }
