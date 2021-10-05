from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoMexicoCityINFOCDMX(MexicoINAIBase):
    """
    Domain
      Instituto de Transparencia, Acceso a la Información Pública, Protección de Datos Personales y Rendición de Cuentas
      de la Ciudad de México (INFOCDMX)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2019'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2021'.
    API documentation
      https://dashboard.infocdmx.org.mx/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_mexico_city_infocdmx'

    # BaseSpider
    default_from_date = '2019'
    default_until_date = '2021'

    # PeriodicSpider
    pattern = 'https://contratacionesabiertas.infocdmx.org.mx:3000/edca/contractingprocess/{}'
