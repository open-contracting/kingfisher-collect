from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoSinaloaCEAIP(MexicoINAIBase):
    """
    Domain
      Comisión Estatal para el Acceso a la Información Pública (CEAIP)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2021'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      http://ceaipsinaloa.ddns.net:4000/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_sinaloa_ceaip'

    # BaseSpider
    default_from_date = '2021'

    # MexicoINAIBase
    base_url = 'http://ceaipsinaloa.ddns.net:3000'
