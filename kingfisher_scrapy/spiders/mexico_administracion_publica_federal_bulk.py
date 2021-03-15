from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components


class MexicoAPFBulk(CompressedFileSpider):
    """
    Domain
      Administración Pública Federal (APF) - Secretaria de la Función Pública (SFP) - Secretaría de Hacienda y Crédito
      Público (SHCP)
    Bulk download documentation
      https://datos.gob.mx/busca/dataset/concentrado-de-contrataciones-abiertas-de-la-apf
    """
    name = 'mexico_apf_bulk'

    # BaseSpider
    root_path = 'item'

    # CompressedFileSpider
    data_type = 'release'

    def start_requests(self):
        url = 'https://compranetinfo.hacienda.gob.mx/dabiertos/contrataciones_arr.json.zip'
        yield self.build_request(url, formatter=components(-1))
