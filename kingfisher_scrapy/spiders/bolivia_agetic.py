import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error


class BoliviaAgetic(SimpleSpider):
    """
    Domain
      Agencia de Gobierno Electrónico y Tecnologías de Información y Comunicación (AGETIC)
    Spider arguments
      sample
        Downloads the first file in the downloads page.
    Bulk download documentation
      https://datos.gob.bo/id/dataset/contrataciones-agetic-2019-estandar-ocp
    """
    name = 'bolivia_agetic'
    data_type = 'release_list'
    unflatten = True

    def start_requests(self):
        # A CKAN API JSON response.
        url = 'https://datos.gob.bo/api/3/action/package_show?id=contrataciones-agetic-2019-estandar-ocp'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = json.loads(response.text)
        for resource in data['result']['resources']:
            if 'ocds' in resource['description']:
                # Presently, only one URL matches.
                yield scrapy.Request(resource['url'], meta={'file_name': resource['url']}, callback=self.parse_data)

    @handle_http_error
    def parse_data(self, response):
        yield self.build_file(url=response.request.url, data_type=self.data_type, data=response.body)
