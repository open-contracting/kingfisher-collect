import json

import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class MexicoQuienEsQuien(IndexSpider):
    """
    Domain
      QuiénEsQuién.Wiki
    API documentation
      https://quienesquienapi.readthedocs.io/es/latest/
    Swagger API documentation
      https://api.quienesquien.wiki/v2/docs/
    """
    name = 'mexico_quien_es_quien'
    download_delay = 0.9

    # BaseSpider
    root_path = 'item'

    # SimpleSpider
    data_type = 'record_package'

    # IndexSpider
    count_pointer = '/data/0/collections/contracts/count'
    limit = 1000
    base_url = 'https://api.quienesquien.wiki/v2/contracts'
    formatter = staticmethod(parameters('offset'))

    def start_requests(self):
        yield scrapy.Request(
            'https://api.quienesquien.wiki/v2/sources',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse(self, response):
        data = response.json()
        yield self.build_file_from_response(response, data=json.dumps(data['data']).encode(), data_type=self.data_type)
