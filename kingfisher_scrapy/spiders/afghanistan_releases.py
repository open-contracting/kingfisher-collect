from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class AfghanistanReleases(SimpleSpider):
    """
    Domain
      Afghanistan Government Electronic & Open Procurement System (AGEOPS)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2018-12-12'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    API documentation
      https://ocds.ageops.net/
    """
    name = 'afghanistan_releases'
    download_delay = 1.5

    # BaseSpider
    default_from_date = '2018-12-12'
    skip_pluck = 'Already covered (see code for details)'  # afghanistan_release_packages

    # SimpleSpider
    data_type = 'release'

    def start_requests(self):
        # A JSON array of URL strings, in reverse chronological order.
        url = 'https://ocds.ageops.net/api/ocds/releases/dates'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        # A JSON array of URL strings, in reverse chronological order.
        for url in response.json():
            if self.from_date and self.until_date:
                # URL looks like https://ocds.ageops.net/api/ocds/releases/2020-05-30
                date = datetime.strptime(components(-1)(url), self.date_format)
                if not (self.from_date <= date <= self.until_date):
                    continue
            yield self.build_request(url, formatter=components(-1), callback=self.parse_release_list)

    @handle_http_error
    def parse_release_list(self, response):
        for url in response.json():
            # URL looks like https://ocds.ageops.net/api/release/5c10b7d67e0a947b1461057e
            yield self.build_request(url, formatter=components(-1))
