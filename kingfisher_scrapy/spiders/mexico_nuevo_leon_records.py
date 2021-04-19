import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider


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
            meta={'file_name': 'records.json'}
        )
