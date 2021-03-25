import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error, join


class Zambia(CompressedFileSpider):
    """
    Domain
      Zambia Public Procurement Authority
    """
    name = 'zambia'

    # BaseSpider
    ocds_version = '1.0'

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        yield scrapy.Request(
            'https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackagelist',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):

        urls = reversed(response.json()['packagesPerMonth'])

        for url in urls:
            # URL looks like https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackage/2016/7
            yield self.build_request(url, formatter=join(components(-2), extension='zip'))
