import hashlib
from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_error


class KenyaMakueni(SimpleSpider):
    """
    Swagger API documentation
        https://opencontracting.makueni.go.ke/swagger-ui.html#/ocds-controller
    Spider arguments
      sample
        Download only the first 10 release packages in the dataset.
    """
    name = 'kenya_makueni'
    data_type = 'release_package_list'
    url = 'https://opencontracting.makueni.go.ke/api/ocds/package/all?pageSize={}&pageNumber={}'

    def start_requests(self):
        if self.sample:
            url = self.url.format(10, 0)
            yield scrapy.Request(
                url,
                meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
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
            url = self.url.format(page_size, page_number)
            yield scrapy.Request(
                url,
                meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
            )
