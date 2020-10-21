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
    data_type = 'release_package_list'
    limit = 10
    additional_params = {'pageSize': limit}
    yield_list_results = False
    param_page = 'pageNumber'
    formatter = staticmethod(parameters('pageNumber'))

    base_url = 'https://opencontracting.makueni.go.ke/api/ocds/package/all?pageSize={limit}&pageNumber={page}'

    def start_requests(self):
        yield scrapy.Request(
            'https://opencontracting.makueni.go.ke/api/ocds/release/count',
            meta={'file_name': 'count.json'},
            callback=self.parse_list
        )

    def range_generator(self, data, response):
        return range(ceil(int(response.text) / self.limit))

    def url_builder(self, params, data, response):
        return self.pages_url_builder(params, data, response)
