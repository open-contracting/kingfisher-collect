from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class KenyaMakueni(IndexSpider):
    """
    Swagger API documentation
        https://opencontracting.makueni.go.ke/swagger-ui.html#/ocds-controller
    """
    name = 'kenya_makueni'
    data_type = 'release_package_list'
    step = 10
    additional_params = {'pageSize': step}
    yield_list_results = False
    param_page = 'pageNumber'
    formatter = staticmethod(parameters('pageNumber'))

    base_url = 'https://opencontracting.makueni.go.ke/api/ocds/package/all?pageSize={step}&pageNumber={page}'

    def start_requests(self):
        yield scrapy.Request(
            'https://opencontracting.makueni.go.ke/api/ocds/release/count',
            meta={'file_name': 'count.json'},
            callback=self.parse_list
        )

    def range_generator(self, data, response):
        total = int(response.text)
        return range(ceil(total / self.step))

    def url_builder(self, params, data, response):
        return self.pages_url_builder(params, data, response)
