import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider


class MexicoNuevoLeonBase(CompressedFileSpider):
    """
    Bulk download documentation
      https://www.dgcp.gob.do/estandar-mundial-ocds/
    Spider arguments
      sample
        Downloads the co.
    """
    compression = 'rar'

    def start_requests(self):
        yield scrapy.Request(
            'http://si.nl.gob.mx/acceso/DatosAbiertos/JSONsInfraestructuraAbierta.rar',
            meta={'file_name': 'JSONsInfraestructuraAbierta.rar'}
        )
