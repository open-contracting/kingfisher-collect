import json
import scrapy
import hashlib

from kingfisher_scrapy.base_spider import BaseSpider


class MoldovaRecords(BaseSpider):
    name = 'moldova_records'

    def start_requests(self):
        yield scrapy.Request(
            url='http://ocds.mepps.openprocurement.io/api/records.json',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        if response.status == 200:

            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type="record_package")

            if not (hasattr(self, 'sample') and self.sample == 'true'):
                json_data = json.loads(response.body_as_unicode())
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
