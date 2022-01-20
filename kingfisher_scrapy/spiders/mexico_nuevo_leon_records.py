import scrapy

from kingfisher_scrapy.base_spiders.simple_spider import SimpleSpider


class MexicoNuevoLeonRecords(SimpleSpider):
    """
    Domain
      Secretaría de Movilidad y Planeación Urbana de Nuevo León
    Bulk download documentation
      http://si.nl.gob.mx/transparencia/publicaciones
    """
    name = 'mexico_nuevo_leon_records'

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        yield scrapy.Request(
            'http://si.nl.gob.mx/siasi_ws/api/ocds/DescargarRecordPackage',
            meta={'file_name': 'records.json'}
        )
