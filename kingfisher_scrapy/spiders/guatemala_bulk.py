from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import BROWSER_USER_AGENT, components, handle_http_error, join


class GuatemalaBulk(CompressedFileSpider):
    """
    Domain
      Ministerio de Finanzas Públicas - Dirección General de Adquisiciones del Estado
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format).
        If ``until_date`` is provided, defaults to '2020-01'.
      until_date
        Download only data until this month (YYYY-MM format).
        If ``from_date`` is provided, defaults to the current month.
    API documentation
      https://ocds.guatecompras.gt/api-ocds
    Bulk download documentation
      https://ocds.guatecompras.gt/descarga-datos
    """

    name = 'guatemala_bulk'
    user_agent = BROWSER_USER_AGENT  # to avoid HTTP 403

    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2020-01'

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        url = 'https://ocds.guatecompras.gt/files'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        """
        The response looks like:

        {
          "id": "gc-{year}-{month}",
          "results": [
            {
             "files": {
               "csv": "...",
               "sha": "...",
               "json": "...",
               "xlsx": "..."
             },
             "year": "values between 2020 to the current year",
             "month": "values between 1 and 12",
             "monthName": "values between enero to diciembre",
             "source": "Guatecompras",
             "timestamp": "last updated date in timestamp with time zone format"
            }, ...
          ]
        }
        """
        for item in response.json()["result"]:
            if self.from_date and self.until_date:
                date = datetime(int(item['year']), int(item['month']), 1)
                if not (self.from_date <= date <= self.until_date):
                    continue

            yield self.build_request(item['files']['json'], formatter=join(components(-2), extension='zip'))
