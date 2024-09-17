import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class MexicoAdministracionPublicaFederalBulk(CompressedFileSpider):
    """
    Domain
      Administración Pública Federal (APF): Secretaría de Hacienda y Crédito Público (SHCP)
    Caveats
      This data is also published as part of https://www.plataformadigitalnacional.org/contrataciones
    Bulk download documentation
      https://www.gob.mx/compranet/documentos/estandar-de-datos-para-las-contrataciones-abiertas-edca
    """

    name = 'mexico_administracion_publica_federal_bulk'
    download_timeout = 99999  # > 2GB zip file
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False
    }

    # BaseSpider
    root_path = 'item'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            'https://www.gob.mx/compranet/documentos/estandar-de-datos-para-las-contrataciones-abiertas-edca',
            meta={'file_name': 'list.html'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        for url in response.xpath('//a/@href').getall():
            # https://compranetinfo.hacienda.gob.mx/dabiertos/contrataciones_arr.json.zip
            if url.endswith('contrataciones_arr.json.zip'):
                yield self.build_request(url, formatter=components(-1))
