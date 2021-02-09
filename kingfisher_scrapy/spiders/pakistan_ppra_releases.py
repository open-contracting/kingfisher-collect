import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class PakistanPPRAReleases(SimpleSpider):
    """
    Domain
      Pakistan Public Procurement Regulatory Authority (PPRA)
    API documentation
      https://www.ppra.org.pk/api/
    """
    name = 'pakistan_ppra_releases'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            'https://www.ppra.org.pk/api/index.php/api/records',
            meta={'file_name': 'list.html'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        # remove the last item in the list to fix the str JSON format
        urls = json.loads(response.xpath('//body//text()').getall()[6].replace(",\r\n\r\nhttps://www.ppra.org.pk", ""))
        for url in urls:
            yield self.build_request(url, formatter=components(-2))
