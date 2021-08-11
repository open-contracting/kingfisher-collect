from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoZacatecas(MexicoINAIBase):
    """
    Domain
      Instituto Zacatecano de Transparencia y Acceso a la Información (IZAI)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2016'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2021'.
    API documentation
      https://contratacionesabiertas.izai.org.mx/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_zacatecas_izai'

    # BaseSpider
    default_from_date = '2016'
    default_until_date = '2021'

    # PeriodicSpider
    pattern = 'http://128.199.8.41:3000/edca/contractingprocess/{}'
