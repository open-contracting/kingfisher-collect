import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class BoliviaAgetic(SimpleSpider):
    """
    Domain
      Agencia de Gobierno Electrónico y Tecnologías de Información y Comunicación (AGETIC)
    Bulk download documentation
      https://datos.gob.bo/id/dataset/contrataciones-agetic-2019-estandar-ocp
    """
    name = 'bolivia_agetic'

    # BaseSpider
    unflatten = True

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        # A CKAN API JSON response.
        url = 'https://datos.gob.bo/api/3/action/package_show?id=contrataciones-agetic-2019-estandar-ocp'
        yield scrapy.Request(url, meta={'file_name': 'package_show.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for resource in response.json()['result']['resources']:
            if 'ocds' in resource['description']:
                yield self.build_request(resource['url'], formatter=components(-1))
