from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class AfghanistanPackagesBase(SimpleSpider):
    download_delay = 1.5  # for 'too many requests' errors

    # BaseSpider
    default_from_date = '2018-12-15'

    def start_requests(self):
        yield scrapy.Request(self.base_url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        urls = response.json()
        for url in urls:
            if self.from_date and self.until_date:
                # URL looks like https://ocds.ageops.net/api/ocds/release-package/2021-03-29
                date = datetime.strptime(components(-1)(url), self.date_format)
                if not (self.from_date <= date <= self.until_date):
                    continue
            yield self.build_request(url, formatter=components(-2), callback=self.parse_release_list)

    @handle_http_error
    def parse_release_list(self, response):
        urls = response.xpath('//a/text()').getall()
        for url in urls:
            if 'https://ocds.ageops.net/api/' in url:
                yield self.build_request(url.strip(), formatter=components(-2))
