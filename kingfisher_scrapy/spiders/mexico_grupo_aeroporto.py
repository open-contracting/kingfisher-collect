import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider


class MexicoGrupoAeroporto(SimpleSpider):
    name = 'mexico_grupo_aeroporto'
    data_type = 'release_package'

    def start_requests(self):
        url = 'http://gacmda.gacm.mx:8880/files/opendata/coleccion/concentrado05032019RELEASE.json'
        yield scrapy.Request(url, meta={'kf_filename': 'all.json'})
