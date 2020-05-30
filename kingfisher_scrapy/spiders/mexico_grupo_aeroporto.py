import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_error


class MexicoGrupoAeroporto(SimpleSpider):
    name = 'mexico_grupo_aeroporto'
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            'http://gacmda.gacm.mx:8880/files/opendata/coleccion/concentrado05032019RELEASE.json',
            meta={'kf_filename': 'concentrado05032019RELEASE.json'}
        )
