import datetime

import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error, join


class EuropeDynamicSpiderBase(CompressedFileSpider):
    # SimpleSpider
    data_type = 'record_package'
    date_format = 'year-month'

    def start_requests(self):
        yield scrapy.Request(
            self.url,
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        urls = response.json()['packagesPerMonth']
        for url in reversed(urls):
            if self.from_date and self.until_date:
                # URL looks like https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackage/2016/7
                year, month = map(int, url.rsplit('/', 2)[1:])
                url_date = datetime.datetime(year, month, 1)
                if not (self.from_date <= url_date <= self.until_date):
                    continue
            yield self.build_request(url, formatter=join(components(-2), extension='zip'))
