from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class AfghanistanPackagesBase(SimpleSpider):
    default_from_date = '2018-12-15'
    download_delay = 1.5  # for 'too many requests' errors

    def start_requests(self):
        yield scrapy.Request(self.base_url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        urls = response.json()
        for url in urls:
            if self.from_date and self.until_date:
                date = datetime.strptime(url[-10:], "%Y-%m-%d")
                if not (self.from_date <= date <= self.until_date):
                    continue
            yield self.build_request(url, formatter=components(-2), callback=self.parse_release_list)

    @handle_http_error
    def parse_release_list(self, response):
        text_urls = response.xpath('//a/text()').getall()
        urls = list(filter(lambda x: 'https://ocds.ageops.net/api/' in x, text_urls))
        for url in urls:
            yield self.build_request(url.strip(), formatter=components(-2))
