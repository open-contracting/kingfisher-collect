import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class NepalDhangadhi(BaseSpider):
    name = "nepal_dhangadhi"

    def start_requests(self):
        yield scrapy.Request(
            'https://admin.ims.susasan.org/api/static-data/dhangadhi',
            callback=self.parse_item,
        )

    def parse_item(self, response):
        if response.status == 200:
            url = 'https://admin.ims.susasan.org/ocds/json/dhangadhi-{}.json'
            json_data = json.loads(response.text)
            fiscal_years = json_data.get('data').get('fiscal_years')
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
            yield self.save_response_to_disk(
                response,
                response.request.meta['kf_filename'],
                data_type='release_package'
            )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {"http_code": response.status}
            }
