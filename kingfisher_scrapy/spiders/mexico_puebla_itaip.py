from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoPueblaITAIP(MexicoINAIBase):
    """
    Domain
      Instituto de Transparencia, Acceso a la Información Pública y Protección de Datos Personales del Estado de Puebla
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2021'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      http://189.240.12.27:4000/contratacionesabiertas/datosabiertos/
    """
    name = 'mexico_puebla_itaip'

    # BaseSpider
    default_from_date = '2021'

    # MexicoINAIBase
    base_url = 'http://189.240.12.27:3000'
