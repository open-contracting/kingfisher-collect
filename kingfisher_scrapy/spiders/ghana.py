import scrapy

import datetime

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error, join


class Ghana(CompressedFileSpider):
    """
       Domain
         Ghana Electronic Procurement System
       Spider arguments
          from_date
             Download only data from this month onward (YYYY-MM format).
             If ``until_date`` is provided, defaults to '2019-07'.
          until_date
             Download only data until this month (YYYY-MM format).
             If ``from_date`` is provided, defaults to the current month.
    """

    name = 'ghana'

    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2019-07'

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        yield scrapy.Request(
            'https://www.ghaneps.gov.gh/ocds/services/recordpackage/getrecordpackagelist',
            meta={'file_name': 'list.json'},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        urls = response.json()['packagesPerMonth']
        for url in reversed(urls):
            if self.from_date and self.until_date:
                year, month = map(int, url.rsplit('/', 2)[1:])
                url_date = datetime.datetime(year, month, 1)
                if not (self.from_date <= url_date <= self.until_date):
                    continue
            yield self.build_request(url, formatter=join(components(-2), extension='zip'))
