import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class MexicoAdministracionPublicaFederalBulk(CompressedFileSpider):
    """
    Domain
      Administración Pública Federal (APF): Secretaría de Hacienda y Crédito Público (SHCP)
    Bulk download documentation
      https://datos.gob.mx/busca/dataset/concentrado-de-contrataciones-abiertas-de-la-apf
    """
    name = 'mexico_administracion_publica_federal_bulk'
    download_timeout = 99999

    # BaseSpider
    root_path = 'item'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            'https://datos.gob.mx/busca/api/3/action/package_search?q=concentrado-de-contrataciones-abiertas-de-la'
            '-apf',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        for result in data['result']['results']:
            for resource in result['resources']:
                if resource['name'].endswith('JSON.') and resource['format'].upper() == 'JSON':
                    yield self.build_request(resource['url'], formatter=components(-1))
