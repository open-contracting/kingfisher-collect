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

    def start_requests(self):
        url = 'http://ocds.dppib-crsgov.org/Login.aspx?ReturnUrl=%2fReleasePackageViewModel_ListView%2f'
        yield scrapy.Request(url,
                             meta={'page': 0},
                             callback=self.parse_date_list)

    @handle_http_error
    def parse_date_list(self, response):
        # pagination handler
        # page = response.request.meta['page']
        # available_page_list = [re.findall(r"'(.+?)',?", x) for x in
        #                       response.xpath('//a[starts-with(@class,"dxp-num")]/@onclick').extract()]

        available_date_list = [datetime.strptime(date.split('T')[0], '%Y-%m-%d') for date in
                               response.xpath('//tr[@class="dxgvDataRow_XafTheme"]/td[6]/text()').extract()]

        for date in available_date_list:
            for number, url in enumerate(self.build_urls(date)):
                yield self.build_request(url, self.get_formatter(), priority=number * -1)

    def get_formatter(self):
        return join(components(-1), parameters('year', 'month'))

    @abstractmethod
    def build_urls(self, date):
        pass
