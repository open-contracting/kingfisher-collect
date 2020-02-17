import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class Dhangadhi(BaseSpider):
    name = "dhangadhi"

    def start_requests(self):
        yield scrapy.Request(
            'https://admin.ims.susasan.org/api/static-data/dhangadhi',
            callback=self.parse_item,
        )

    def parse_item(self, response):
        if response.status == 200:
            url = 'https://admin.ims.susasan.org/ocds/json/dhangadhi-{}.json'
            fiscal_years = json.loads(response.body_as_unicode()).get('data').get('fiscal_years')
            for item in fiscal_years:
                fy = item.get('name')
                yield scrapy.Request(
                    url.format(fy),
                    meta={'kf_filename': hashlib.md5((url + fy).encode('utf-8')).hexdigest() + '.json'},
                )
                if self.sample:
                    break
        else:
            yield {
                'success': False,
                'url': response.request.url,
                'errors': {"http_code": response.status}
            }

    def parse(self, response):
        if response.status == 200:
            json_data = json.loads(response.body_as_unicode())
            yield self.save_data_to_disk(
                json.dumps(json_data).encode(),
                response.request.meta['kf_filename'],
                data_type='release_package',
                url=response.request.url
            )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {"http_code": response.status}
            }
