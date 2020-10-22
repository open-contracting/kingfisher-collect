import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error, parameters


class MexicoINAI(SimpleSpider):
    """
    Domain
      Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales (INAI)
    Caveats
      Contains data from 2017 only.
    Bulk download documentation
      https://datos.gob.mx/busca/dataset/contrataciones-abiertas-del-inai
    """

    name = 'mexico_inai'
    data_type = 'release_package'
    encoding = 'utf-8-sig'

    def start_requests(self):
        # A CKAN API JSON response.
        yield scrapy.Request(
            'https://datos.gob.mx/busca/api/3/action/package_search?q=organization:inai&rows=500',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        datas = json.loads(response.text)
        for result in datas['result']['results']:
            for resource in result['resources']:
                if resource['format'] == 'JSON':
                    yield self.build_request(resource['url'], formatter=components(-1), meta={'dont_redirect': True},
                                             callback=self.parse_redirect)

    def parse_redirect(self, response):
        if response.status == 301:
            url = response.headers['Location'].decode('utf-8').replace('open?', 'uc?export=download&')
            yield self.build_request(url, formatter=parameters('id'))
        else:
            yield self.build_file_error_from_response(response)
