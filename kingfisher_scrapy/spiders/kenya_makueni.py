import hashlib
from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


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

    @handle_error
    def parse_count(self, response):
        total = int(response.text)
        page_size = 300

        for page_number in range((ceil(total / page_size))):
            yield scrapy.Request(
                self.url.format(page_size, page_number),
                meta={'kf_filename': hashlib.md5((self.url +
                                                  str(page_number)).encode('utf-8')).hexdigest() + '.json'}
            )

    @handle_error
    def parse(self, response):
        yield self.build_file_from_response(response, response.request.meta['kf_filename'],
                                            data_type='release_package_list')
