import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider


class MexicoNuevoLeonBase(CompressedFileSpider):
    """
    Base class to download Mexico Nuevo Leon data
    """
    compression = 'rar'

    def start_requests(self):
        yield scrapy.Request(
            'http://si.nl.gob.mx/acceso/DatosAbiertos/JSONsInfraestructuraAbierta.rar',
            meta={'file_name': 'JSONsInfraestructuraAbierta.rar'}
        )
