from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components


class MexicoNuevoLeonBase(CompressedFileSpider):
    """
    Base class to download Mexico Nuevo Leon data
    """
    compression = 'rar'

    def start_requests(self):
        yield self.build_request(
            'http://si.nl.gob.mx/acceso/DatosAbiertos/JSONsInfraestructuraAbierta.rar',
            formatter=components(-1)
        )
