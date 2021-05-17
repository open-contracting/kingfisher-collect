"""
This spider deliberately generates one mocked release package.
"""
import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error


class Succeed(SimpleSpider):
    name = 'succeed'

    # BaseSpider
    skip_pluck = 'Not a real spider'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request('https://example.com', meta={'file_name': 'all.json'})

    @handle_http_error
    def parse(self, response):
        yield self.build_file(data={'releases': [{'date': '2020-05-13T00:00:00Z'}]},
                              data_type=self.data_type,
                              file_name='data.json', url=response.request.url)
