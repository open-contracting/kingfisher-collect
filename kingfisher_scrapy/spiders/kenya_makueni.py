from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class KenyaMakueni(IndexSpider):
    """
    Domain
      Makueni County
    Swagger API documentation
      https://opencontracting.makueni.go.ke/swagger-ui.html#/ocds-controller
    """
    name = 'kenya_makueni'

    # BaseSpider
    root_path = 'item'

    # SimpleSpider
    data_type = 'release_package'

    # IndexSpider
    limit = 10
    formatter = staticmethod(parameters('pageNumber'))
    param_page = 'pageNumber'
    yield_list_results = False
    parse_list_loader = int
    base_url = 'https://opencontracting.makueni.go.ke/api/ocds/package/all?pageSize=10'

    def start_requests(self):
        yield scrapy.Request(
            'https://opencontracting.makueni.go.ke/api/ocds/release/count',
            meta={'file_name': 'count.json'},
            callback=self.parse_list
        )

    def range_generator(self, data, response):
        return range(ceil(data / self.limit))

    def url_builder(self, value, data, response):
        return self.pages_url_builder(value, data, response)
