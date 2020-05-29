import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class MexicoGrupoAeroporto(BaseSpider):
    name = 'mexico_grupo_aeroporto'

    def start_requests(self):
        yield scrapy.Request(
            url='http://gacmda.gacm.mx:8880/files/opendata/coleccion/concentrado05032019RELEASE.json',
            meta={'kf_filename': 'concentrado05032019RELEASE.json'}
        )

    @handle_error
    def parse(self, response):
        yield self.build_file_from_response(response, data_type='release_package')
