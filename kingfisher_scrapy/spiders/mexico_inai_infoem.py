from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoINAIINFOEM(MexicoINAIBase):
    """
    Domain
      Instituto de Transparencia, Acceso a la Información Pública y
      Protección de Datos Personales del Estado de México y Municipios
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2021'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2021'.
    API documentation
      http://www.infoem.org.mx:4000/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_infoem'

    # BaseSpider
    default_from_date = '2021'
    default_until_date = '2021'

    # PeriodicSpider
    pattern = 'http://infoem.org.mx:3000/edca/contractingprocess/{}'
