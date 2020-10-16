import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class MexicoAdministracionPublicaFederal(IndexSpider):
    """
    Bulk download documentation
      https://datos.gob.mx/busca/dataset/concentrado-de-contrataciones-abiertas-de-la-apf
    Spider arguments
      sample
        Sets the number of record packages to download.
    """
    name = 'mexico_administracion_publica_federal'
    data_type = 'record_package_list_in_results'
    count_pointer = '/pagination/total'
    limit = '/pagination/pageSize'
    use_page = True
    formatter = staticmethod(parameters('page'))

    def start_requests(self):
        url = 'https://api.datos.gob.mx/v1/contratacionesabiertas'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)
