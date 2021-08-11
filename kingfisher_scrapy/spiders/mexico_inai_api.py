from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoINAIAPI(MexicoINAIBase):
    """
    Domain
      Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales (INAI)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2015'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2021'.
    API documentation
      http://contratacionesabiertas.inai.org.mx/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_inai_api'

    # BaseSpider
    default_from_date = '2015'
    default_until_date = '2021'

    # PeriodicSpider
    pattern = 'http://contratacionesabiertas.inai.org.mx:3000/edca/contractingprocess/{}'
