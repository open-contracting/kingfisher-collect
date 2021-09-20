from abc import abstractmethod
from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters


class NigeriaCrossRiverBase(SimpleSpider):
    # SimpleSpider
    base_url = 'http://ocdsapi.dppib-crsgov.org/api/ocdsAPI/'

    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2021-02'

    formatter = staticmethod(join(components(-1), parameters('year', 'month')))

    def start_requests(self):
        url = 'http://ocdsapi.dppib-crsgov.org/api/ocdsAPI/getAvailableReleasesSummary'
        yield scrapy.Request(url, meta={'file_name': 'list.json'})

    @handle_http_error
    def parse(self, response):
        for item in response.json():
            date = datetime(item['year'], item['month'], 1)
            for number, url in enumerate(self.build_urls(date)):
                yield self.build_request(url, formatter=self.formatter, callback=super().parse, priority=number * -1)

    @abstractmethod
    def build_urls(self, date):
        pass
