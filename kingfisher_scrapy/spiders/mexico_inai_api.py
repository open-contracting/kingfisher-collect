from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoINAIAPI(MexicoINAIBase):
    """
    Domain
      Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales (INAI)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2015'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      http://contratacionesabiertas.inai.org.mx/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_inai_api'
    base_url = 'http://contratacionesabiertas.inai.org.mx:3000'

    # BaseSpider
    default_from_date = '2015'
