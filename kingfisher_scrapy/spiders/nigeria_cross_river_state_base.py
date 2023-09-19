from abc import abstractmethod
from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters


class NigeriaCrossRiverStateBase(SimpleSpider):
    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2019-08'

    # Local
    url_prefix = 'https://ocdsapi.dppib-crsgov.org/api/ocdsAPI/'

    def start_requests(self):
        url = f'{self.url_prefix}getAvailableReleasesSummary'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        formatter = join(components(-1), parameters('year', 'month'))  # format
        for item in response.json():
            date = datetime(item['year'], item['month'], 1)

            if self.from_date and self.until_date:
                if not (self.from_date <= date <= self.until_date):
                    continue

            yield self.build_request(self.build_url(date), formatter=formatter)

    @abstractmethod
    def build_url(self, date):
        pass
