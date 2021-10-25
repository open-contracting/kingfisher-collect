from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoQuintanaRooIDAIP(MexicoINAIBase):
    """
    Domain
      Instituto de Acceso a la Información y Protección de Datos Personales de Quintana Roo (IDAIPQROO)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2020'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2021'.
    API documentation
      http://conab.idaipqroo.org.mx:4000/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_quintana_roo_idaip'

    # BaseSpider
    default_from_date = '2020'
    default_until_date = '2021'

    # PeriodicSpider
    pattern = 'http://conab.idaipqroo.org.mx:3000/edca/contractingprocess/{}'
