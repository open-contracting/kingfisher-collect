import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class DominicanRepublic(CompressedFileSpider):
    name = 'dominican_republic'
    data_type = 'release_package'
    compressed_file_format = 'release_package'
    archive_format = 'rar'

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

        for url in json_urls:
            if '/JSON_DGCP_' in url:
                yield self.build_request(url, formatter=components(-1))
