from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components


class MexicoNuevoLeonBase(CompressedFileSpider):
    def start_requests(self):
        yield self.build_request(
            'http://si.nl.gob.mx/acceso/DatosAbiertos/JSONsInfraestructuraAbierta.rar',
            formatter=components(-1)
        )
