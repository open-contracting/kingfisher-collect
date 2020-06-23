import json
from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters, replace_parameter


class MexicoAdministracionPublicaFederal(SimpleSpider):
    """
    Bulk download documentation
      https://datos.gob.mx/busca/dataset/concentrado-de-contrataciones-abiertas-de-la-apf
    Spider arguments
      sample
        Download only 100 records.
    """
    name = 'mexico_administracion_publica_federal'
    data_type = 'record_package_list_in_results'

    def start_requests(self):
        url = 'https://api.datos.gob.mx/v1/contratacionesabiertas'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        yield from self.parse(response)

        if not self.sample:
            data = json.loads(response.text)
            page = data['pagination']['page']
            total = data['pagination']['total']
            limit = data['pagination']['pageSize']
            for page in range(page + 1, ceil(total / limit)):
                url = replace_parameter(response.request.url, 'page', page)
                yield self.build_request(url, formatter=parameters('page'))
