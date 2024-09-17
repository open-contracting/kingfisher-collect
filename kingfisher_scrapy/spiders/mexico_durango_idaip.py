from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoDurangoIDAIP(MexicoINAIBase):
    """
    Domain
      Instituto Duranguense de Acceso a la Información y de Protección de Datos Personales (IDAIP)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2020'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      http://contratacionesabiertas.idaip.org.mx/contratacionesabiertas/datosabiertos
    """

    name = 'mexico_durango_idaip'

    # BaseSpider
    default_from_date = '2020'

    # MexicoINAIBase
    base_url = 'http://74.208.135.52:3000'
