import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class SpainZaragoza(SimpleSpider):
    """
    Domain
      Ayuntamiento de Zaragoza
    Caveats
      The API's before and after query string parameters have no effect and are therefore not implemented.
    Swagger API documentation
      https://www.zaragoza.es/docs-api_sede/
    """
    name = 'spain_zaragoza'

    # SimpleSpider
    data_type = 'release_package'

    # Local
    url_prefix = 'https://www.zaragoza.es/sede/servicio/contratacion-publica/ocds/contracting-process/'

    def start_requests(self):
        # row parameter setting to 100000 to get all releases
        url = f'{self.url_prefix}?rf=html&rows=100000'

        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for item in response.json():
            yield self.build_request(f'{self.url_prefix}{item["ocid"]}', formatter=components(-1))  # ocid
