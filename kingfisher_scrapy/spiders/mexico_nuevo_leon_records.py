import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class MexicoNuevoLeonRecords(SimpleSpider):
    """
    Domain
      Secretaría de Infraestructura del Gobierno del Estado de Nuevo León
    Bulk download documentation
      http://si.nl.gob.mx/transparencia/publicaciones
    """
    name = 'mexico_nuevo_leon_records'

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        yield scrapy.Request(
            'http://si.nl.gob.mx/siasi_ws/api/ocds/DescargarRecordPackage?usuario=undefined&servidor=undefined',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        content = response.json()
        url = content['urlWebOcdspackage']
        if url:
            yield self.build_request(url, formatter=components(-1))
