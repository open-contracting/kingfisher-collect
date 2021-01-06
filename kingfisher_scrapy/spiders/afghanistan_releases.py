from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components, handle_http_error


class AfghanistanReleases(PeriodicSpider):
    """
    Domain
      Afghanistan Government Electronic & Open Procurement System (AGEOPS)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM-DD format). Defaults to '2018-12-12'.
      until_date
        Download only data until this month (YYYY-MM-DD format). Defaults to the current date.
    API documentation
      https://ocds.ageops.net/
    """
    name = 'afghanistan_releases'
    data_type = 'release'

    # PeriodicSpider variables
    default_from_date = '2018-12-12'
    pattern = 'https://ocds.ageops.net/api/ocds/releases/{}'
    start_requests_callback = 'parse_list'

    download_delay = 1.5

    @handle_http_error
    def parse_list(self, response):
        urls = response.json()
        for url in urls:
            # URL looks like https://ocds.ageops.net/api/release/5ed2a62c4192f32c8c74a4e3
            yield self.build_request(url, self.get_formatter())

    def get_formatter(self):
        return components(-1)
