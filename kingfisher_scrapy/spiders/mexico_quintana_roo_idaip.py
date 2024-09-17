import scrapy

from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoQuintanaRooIDAIP(MexicoINAIBase):
    """
    Domain
      Instituto de Acceso a la Información y Protección de Datos Personales de Quintana Roo (IDAIPQROO)
    API documentation
      http://conab.idaipqroo.org.mx:4000/contratacionesabiertas/datosabiertos
    """

    name = 'mexico_quintana_roo_idaip'

    # MexicoINAIBase
    base_url = 'http://conab.idaipqroo.org.mx:3000'

    def start_requests(self):
        yield scrapy.Request(f'{self.base_url}/edca/contractingprocess/null', meta={'file_name': 'all.json'})
