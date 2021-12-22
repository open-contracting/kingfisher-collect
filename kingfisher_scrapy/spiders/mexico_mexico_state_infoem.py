from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoMexicoStateINFOEM(MexicoINAIBase):
    """
    Domain
      Instituto de Transparencia, Acceso a la Información Pública y Protección de Datos Personales del Estado de México
      y Municipios (INFOEM)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2021'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      http://www.infoem.org.mx:4000/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_mexico_state_infoem'

    # BaseSpider
    default_from_date = '2021'

    # MexicoINAIBase
    base_url = 'http://infoem.org.mx:3000'
