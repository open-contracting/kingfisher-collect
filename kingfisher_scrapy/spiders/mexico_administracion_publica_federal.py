import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class MexicoAdministracionPublicaFederal(IndexSpider):
    """
    Domain
      Administración Pública Federal (APF)
    Bulk download documentation
      https://datos.gob.mx/busca/dataset/concentrado-de-contrataciones-abiertas-de-la-apf
    """
    name = 'mexico_administracion_publica_federal'

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
