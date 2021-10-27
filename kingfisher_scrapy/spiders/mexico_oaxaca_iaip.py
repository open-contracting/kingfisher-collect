from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoOaxacaIAIP(MexicoINAIBase):
    """
    Domain
      Instituto de Acceso a la Información Publica y Protección de Datos Personales del Estado de Oaxaca (IAIPOXACA)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2021'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      http://contratacionesabiertas-iaipoaxaca-org.mx:4000/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_oaxaca_iaip'
    domain_pattern = 'http://contratacionesabiertas-iaipoaxaca-org.mx:3000{}'
