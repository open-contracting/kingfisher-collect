import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class SpainZaragoza(SimpleSpider):
    """
    Caveats
      The API before and after query string parameters have no effect and are therefore not implemented.
    Domain
      Ayuntamiento de Zaragoza
    Swagger API documentation
      https://www.zaragoza.es/docs-api_sede/
    """
    name = 'spain_zaragoza'
    data_type = 'release_package'
    url = 'https://www.zaragoza.es/sede/servicio/contratacion-publica/ocds/contracting-process/'

    def start_requests(self):
        # row parameter setting to 100000 to get all releases
        url = f'{self.url}?rf=html&rows=100000'

        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        ids = json.loads(response.text)
        for contracting_process_id in ids:
            ocid = contracting_process_id['ocid']
            url = f'{self.url}{ocid}'
            yield self.build_request(url, formatter=components(-1))
