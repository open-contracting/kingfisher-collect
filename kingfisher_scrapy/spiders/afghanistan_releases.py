import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class AfghanistanReleases(SimpleSpider):
    """
    API documentation
      https://ocds.ageops.net/
    """
    name = 'afghanistan_releases'
    data_type = 'release'

    download_delay = 1.5

    def start_requests(self):
        # A JSON array of URL strings, in reverse chronological order.
        url = 'https://ocds.ageops.net/api/ocds/releases/dates'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        urls = json.loads(response.text)
        for url in urls:
            # A JSON array of URL strings, in reverse chronological order.
            # URL looks like https://ocds.ageops.net/api/ocds/releases/2020-05-30
            yield self.build_request(url, formatter=components(-1), callback=self.parse_release_list)

    @handle_http_error
    def parse_release_list(self, response):
        urls = json.loads(response.text)
        for url in urls:
            # URL looks like https://ocds.ageops.net/api/release/5ed2a62c4192f32c8c74a4e3
            yield self.build_request(url, formatter=components(-1))
