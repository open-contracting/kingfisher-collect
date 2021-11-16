from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoQuintanaRooIDAIP(MexicoINAIBase):
    """
    Domain
      Instituto de Acceso a la Información y Protección de Datos Personales de Quintana Roo (IDAIPQROO)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2020'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      http://conab.idaipqroo.org.mx:4000/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_quintana_roo_idaip'
    base_url = 'http://conab.idaipqroo.org.mx:3000'

    # BaseSpider
    default_from_date = '2020'
