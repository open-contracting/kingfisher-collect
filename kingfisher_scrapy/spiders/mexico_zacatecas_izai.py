from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoZacatecasIZAI(MexicoINAIBase):
    """
    Domain
      Instituto Zacatecano de Transparencia y Acceso a la Información (IZAI)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2016'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      https://contratacionesabiertas.izai.org.mx/contratacionesabiertas/datosabiertos
    """

    name = 'mexico_zacatecas_izai'

    # BaseSpider
    default_from_date = '2016'

    # MexicoINAIBase
    base_url = 'http://128.199.8.41:3000'
