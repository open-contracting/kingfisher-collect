import hashlib
import json
from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class KenyaMakueni(BaseSpider):
    name = 'kenya_makueni'
    url = 'https://opencontracting.makueni.go.ke/api/ocds/package/all?pageSize={}&pageNumber={}'

    def start_requests(self):
        if self.sample:
            page_number = 0
            page_size = 10
            yield scrapy.Request(
                self.url.format(page_size, page_number),
                meta={'kf_filename': hashlib.md5((self.url +
                                                  str(page_number)).encode('utf-8')).hexdigest() + '.json'}
            )
        else:
            yield scrapy.Request(
                'https://opencontracting.makueni.go.ke/api/ocds/release/count',
                meta={'kf_filename': 'start_requests'},
                callback=self.parse_count
            )

    def parse_count(self, response):
        if response.status == 200:
            total = int(response.text)
            page_size = 300

            for page_number in range((ceil(total / page_size))):
                yield scrapy.Request(
                    self.url.format(page_size, page_number),
                    meta={'kf_filename': hashlib.md5((self.url +
                                                      str(page_number)).encode('utf-8')).hexdigest() + '.json'}
                )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }

    def parse(self, response):
        if response.status == 200:
            json_data = json.loads(response.text)
            yield self.save_data_to_disk(
                json.dumps(json_data).encode(),
                response.request.meta['kf_filename'],
                data_type='release_package_list',
                url=response.request.url
            )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
