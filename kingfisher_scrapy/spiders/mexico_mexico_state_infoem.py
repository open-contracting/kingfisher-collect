import scrapy

from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoMexicoStateINFOEM(MexicoINAIBase):
    """
    Domain
      Instituto de Transparencia, Acceso a la Información Pública y Protección de Datos Personales del Estado de México
      y Municipios (INFOEM)
    API documentation
      http://www.infoem.org.mx:4000/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_mexico_state_infoem'

    # MexicoINAIBase
    base_url = 'http://infoem.org.mx:3000'

    def start_requests(self):
        yield scrapy.Request(f'{self.base_url}/edca/contractingprocess/null', meta={'file_name': 'all.json'})
