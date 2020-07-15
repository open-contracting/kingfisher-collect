import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class DominicanRepublic(CompressedFileSpider):
    """
    Bulk download documentation
      https://www.dgcp.gob.do/estandar-mundial-ocds/
    Spider arguments
      sample
        Downloads a release package for the oldest year (2018, first link in the downloads page).
    """
    name = 'dominican_republic'
    data_type = 'release_package'
    zip_file_format = 'release_package'
    compression = 'rar'

    def start_requests(self):
        yield scrapy.Request(
            'https://www.dgcp.gob.do/estandar-mundial-ocds/',
            meta={'file_name': 'list.html'},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        urls = response.css('.fileLink::attr(href)').getall()
        json_urls = list(filter(lambda x: '/JSON_DGCP_' in x, urls))

        if self.sample and len(json_urls) > 0:
            json_urls = [json_urls[0]]

        for url in json_urls:
            if '/JSON_DGCP_' in url:
                yield self.build_request(url, formatter=components(-1))
