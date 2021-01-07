import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class AfghanistanRecords(SimpleSpider):
    """
    Domain
      Afghanistan Government Electronic & Open Procurement System (AGEOPS)
    API documentation
      https://ocds.ageops.net/
    """
    name = 'afghanistan_records'
    data_type = 'record'
    skip_pluck = 'Already covered (see code for details)'  # afghanistan_releases

    download_delay = 1

    def start_requests(self):
        # A JSON array of URL strings, in reverse chronological order.
        url = 'https://ocds.ageops.net/api/ocds/records'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        urls = response.json()
        for url in urls:
            # URL looks like https://ocds.ageops.net/api/record/5ed2a62c4192f32c8c74a4e5
            yield self.build_request(url, formatter=components(-1))
