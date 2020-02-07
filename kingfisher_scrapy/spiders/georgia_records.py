import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class GeorgiaRecords(BaseSpider):
    name = 'georgia_records'
    start_urls = ['https://odapi.spa.ge/api/records.json']

    def start_requests(self):
        yield scrapy.Request(
            url='https://odapi.spa.ge/api/records.json',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        if response.status == 200:

            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type="record_package")

            json_data = json.loads(response.text)
            if not (hasattr(self, 'sample') and self.sample == 'true'):
                if 'links' in json_data and 'next' in json_data['links']:
                    url = json_data['links']['next']
                    yield scrapy.Request(
                        url=url,
                        meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest()+'.json'}
                    )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
