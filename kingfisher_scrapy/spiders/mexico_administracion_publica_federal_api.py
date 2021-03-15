import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class MexicoAdministracionPublicaFederalAPI(IndexSpider):
    """
    Domain
      Administración Pública Federal (APF): Secretaria de la Función Pública (SFP) - Secretaría de Hacienda y Crédito
      Público (SHCP)
    API documentation
      https://www.datos.gob.mx/busca/dataset/api-de-contrataciones-abiertas-de-la-apf
    """
    name = 'mexico_administracion_publica_federal_api'

    # BaseSpider
    root_path = 'results.item'

    # SimpleSpider
    data_type = 'record_package'

    # IndexSpider
    count_pointer = '/pagination/total'
    limit = '/pagination/pageSize'
    use_page = True
    formatter = staticmethod(parameters('page'))

    def start_requests(self):
        url = 'https://api.datos.gob.mx/v2/contratacionesabiertas'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)
