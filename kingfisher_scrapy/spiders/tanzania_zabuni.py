import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class TanzaniaZabuni(SimpleSpider):
    """
    Domain
      Tanzania Zabuni
    API documentation
      https://zabuni.co.tz/docs
    """
    name = 'tanzania_zabuni'
    download_delay = 1  # to avoid API 429 error "too many request"

    # SimpleSpider
    data_type = 'release_package'

    url_prefix = 'https://app.zabuni.co.tz/api/releases/'

    def start_requests(self):
        stages = ['tender', 'award', 'contract']
        for stage in stages:
            yield scrapy.Request(
                f'{self.url_prefix}{stage}',
                meta={'file_name': 'list.json', 'stage': stage},
                callback=self.parse_list
            )

    @handle_http_error
    def parse_list(self, response):
        for release in response.json()['releases']:
            yield self.build_request(
                f'{self.url_prefix}{release["ocid"]}/{response.request.meta["stage"]}',
                formatter=components(-2)
            )
