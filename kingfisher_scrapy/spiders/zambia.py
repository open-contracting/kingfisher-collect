import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class Zambia(CompressedFileSpider):
    """
    Domain
      Zambia Public Procurement Authority
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2016-07'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    """
    name = 'zambia'
    date_format = 'year-month'
    default_from_date = '2016-07'

    # BaseSpider
    ocds_version = '1.0'

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        yield scrapy.Request(
            'https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackagelist',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        urls = response.json()['packagesPerMonth']
        for url in urls:
            if self.from_date and self.until_date:
                year = int(url[69:73])
                month = int(url[74:])
                if not ((self.from_date.year <= year <= self.until_date.year)
                        and (self.from_date.month <= month <= self.until_date.month)):
                    continue
            # URL looks like https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackage/2016/7
            yield self.build_request(url, formatter=components(-2))
