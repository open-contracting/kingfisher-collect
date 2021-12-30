import datetime
from urllib.parse import urlsplit

import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error, join


class EuropeanDynamicsBase(CompressedFileSpider):

    """
    This class makes it easy to collect data from an European Dynamics' Electronic Procurement API:

    #. Inherit from ``EuropeanDynamicsBase``
    #. Set a ``base_url`` class attribute with the portal's domain
    #. Set a ``default_from_date`` class attribute with the initial date (year-month) to scrape

    .. code-block:: python

        from kingfisher_scrapy.spiders.europe_dynamic_base import EuropeanDynamicsBase

        class MySpider(EuropeanDynamicsBase):
            name = 'my_spider'

            # BaseSpider
            default_from_date = '2019-07'

            # EuropeanDynamicsBase
            base_url = 'http://base-url'

    """

    # SimpleSpider
    data_type = 'record_package'
    date_format = 'year-month'

    def start_requests(self):
        yield scrapy.Request(
            f'{self.base_url}/ocds/services/recordpackage/getrecordpackagelist',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        urls = response.json()['packagesPerMonth']
        for number, url in enumerate(reversed(urls)):
            path = urlsplit(url).path
            if self.from_date and self.until_date:
                # URL looks like https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackage/2016/7
                year, month = map(int, url.rsplit('/', 2)[1:])
                url_date = datetime.datetime(year, month, 1)
                if not (self.from_date <= url_date <= self.until_date):
                    continue
            yield self.build_request(f'{self.base_url}{path}', formatter=join(components(-2), extension='zip'),
                                     priority=number * -1)
