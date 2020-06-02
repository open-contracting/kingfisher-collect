from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class KenyaMakueni(SimpleSpider):
    name = 'kenya_makueni'
    data_type = 'release_package_list'
    step = 10

    url = 'https://opencontracting.makueni.go.ke/api/ocds/package/all?pageSize={step}&pageNumber={page}'

    def start_requests(self):
        if self.sample:
            url = self.url.format(step=self.step, page=0)
            yield self.build_request(url, formatter=parameters('pageNumber'))
        else:
            yield scrapy.Request(
                'https://opencontracting.makueni.go.ke/api/ocds/release/count',
                meta={'kf_filename': 'count.json'},
                callback=self.parse_count
            )

    @handle_http_error
    def parse_count(self, response):
        total = int(response.text)
        for page in range(ceil(total / self.step)):
            url = self.url.format(step=self.step, page=page)
            yield self.build_request(url, formatter=parameters('pageNumber'))
