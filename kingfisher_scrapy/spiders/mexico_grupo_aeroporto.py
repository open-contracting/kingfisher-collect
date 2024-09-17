import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider


class MexicoGrupoAeroporto(SimpleSpider):
    """
    Domain
      Grupo Aeroportuario de la Ciudad de México (CDMX)
    """

    name = 'mexico_grupo_aeroporto'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = 'http://gacmda.gacm.mx:8880/files/opendata/coleccion/concentrado05032019RELEASE.json'
        yield scrapy.Request(url, meta={'file_name': 'all.json'})
