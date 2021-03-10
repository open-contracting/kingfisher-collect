import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class MexicoAPFAPI(IndexSpider):
    """
    Domain
      Administración Pública Federal (APF) - Secretaria de la Función Pública (SFP) - Secretaría de Hacienda y Crédito
      Público (SHCP)
    """
    name = 'mexico_apf_api'

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
        url = 'https://api.datos.gob.mx/v1/contratacionesabiertas'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)
