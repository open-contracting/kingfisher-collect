import datetime
from json import JSONDecodeError
from urllib.parse import urlsplit

import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error, join


class EuropeanDynamicsBase(CompressedFileSpider):
    """
    Collect data from a European Dynamics Electronic Procurement API:

    #. Inherit from ``EuropeanDynamicsBase``
    #. Set a ``base_url`` class attribute with the portal's domain
    #. Set a ``default_from_date`` class attribute with the initial date (year-month) to scrape

    .. code-block:: python

        from kingfisher_scrapy.spiders.european_dynamics_base import EuropeanDynamicsBase

        class MySpider(EuropeanDynamicsBase):
            name = 'my_spider'

            # BaseSpider
            default_from_date = '2019-07'

            # EuropeanDynamicsBase
            base_url = 'http://base-url'
    """

    # SimpleSpider
    data_type = "record_package"
    date_format = "year-month"

    # base_url must be provided by subclasses.

    async def start(self):
        yield scrapy.Request(
            f"{self.base_url}/ocds/services/recordpackage/getrecordpackagelist",
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        try:
            data = response.json()
        # The response can be an HTML document with an error message like "temporary unavailable due to maintenance".
        except JSONDecodeError as e:
            self.log_error_from_response(response, level="exception", message=e)
            return

        for number, url in enumerate(reversed(data["packagesPerMonth"])):
            path = urlsplit(url).path
            if self.from_date and self.until_date:
                # URL looks like https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackage/2016/7
                year, month = map(int, url.rsplit("/", 2)[1:])
                url_date = datetime.datetime(year, month, 1)
                if not (self.from_date <= url_date <= self.until_date):
                    continue
            yield self.build_request(
                f"{self.base_url}{path}", formatter=join(components(-2), extension="zip"), priority=number * -1
            )
