import json

import scrapy

from kingfisher_scrapy.spiders.honduras_portal_base import HondurasPortalBase
from kingfisher_scrapy.util import handle_http_error, components


class PackistanPPRARecords(SimpleSpider):
    """
    Domain
      Pakistan Public Procurement Regulatory Authority (PPRA)
    API documentation
      https://www.ppra.org.pk/api/
    """
    name = 'pakistan_ppra_records'
    data_type = 'record_package'

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
