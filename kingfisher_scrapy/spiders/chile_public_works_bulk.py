from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import components


class ChilePublicWorksBUlk(CompressedFileSpider):
    """
    Domain
      Observatorio del Gasto Fiscal - Dirección General de Obras Públicas
    Bulk download documentation
      https://obrapublica.cl/Data/
    """

    name = 'chile_public_works_bulk'

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        yield self.build_request('https://obrapublica.cl/download/ocds_descargamasiva.zip', formatter=components(-1))
