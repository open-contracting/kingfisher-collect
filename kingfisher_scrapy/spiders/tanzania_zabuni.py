import json
from os.path import join as join_path

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error, join


class TanzaniaZabuni(SimpleSpider):
    """
    Domain
      Tanzania Zabuni
    API documentation
      https://zabuni.co.tz/docs
    """
    name = 'tanzania_zabuni'
    data_type = 'release_package'
    url = 'https://app.zabuni.co.tz/api/releases/{}'
    download_delay = 1

    def start_requests(self):
        stages = ['tender', 'award', 'contract']
        for stage in stages:
            yield scrapy.Request(
                self.url.format(stage),
                meta={'file_name': 'list.json', 'stage': stage},
                callback=self.parse_list
            )

    @handle_http_error
    def parse_list(self, response):
        releases = json.loads(response.text)['releases']
        for release in releases:
            yield self.build_request(
                self.url.format(join_path(release['ocid'], response.request.meta['stage'])),
                formatter=join(components(-1), components(-2, -1))
            )
