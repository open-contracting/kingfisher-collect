import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class Italy(SimpleSpider):
    """
    Domain
      AppaltiPOP
    Bulk download documentation
      https://www.appaltipop.it/it/download
    """
    name = 'italy'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            'https://www.appaltipop.it/it/download',
            meta={'file_name': 'list.html'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        html_urls = response.xpath('//a/@href').getall()
        for html_url in html_urls:
            if '.json' in html_url:
                yield self.build_request(html_url, formatter=components(-2))
