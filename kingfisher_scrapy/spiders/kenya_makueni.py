import hashlib
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
            yield self.build_file_error_from_response(response)

    def parse(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(
                response,
                response.request.meta['kf_filename'],
                data_type='release_package_list'
            )

        else:
            yield self.build_file_error_from_response(response)
