from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class EuropeTedTenderBase(IndexSpider):
    """
    Domain
      TenderBase
    API endpoints
      Get releases by page
        Link
          ``http://www.tenderbase.eu/api/releases/?page={page}``
        Parameters
          page
            page number
    """
    name = 'europe_ted_tender_base'

    # BaseSpider
    ocds_version = '1.1'

    # SimpleSpider
    data_type = 'release_package'

    # IndexSpider
    limit = 10
    formatter = staticmethod(parameters('page'))
    param_page = 'page'
    yield_list_results = False

    base_url = 'http://www.tenderbase.eu/api/releases/?&page={page}'

    def start_requests(self):
        yield scrapy.Request(
            'http://www.tenderbase.eu/releases/',
            meta={'file_name': 'count.json'},
            callback=self.parse_list
        )

    def range_generator(self, data, response):
        count_releases = response.xpath('//div[@class="container my-4"]//span/span/text()').get()
        return range(ceil(int(count_releases) / self.limit))

    def url_builder(self, value, data, response):
        return self.pages_url_builder(value, data, response)
