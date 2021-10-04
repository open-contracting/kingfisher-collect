from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoOaxacaIAIPO(MexicoINAIBase):
    """
    Domain
      Instituto de Acceso a la Información Publica y Protección de Datos Personales del Estado de Oaxaca (IAIPOXACA)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2021'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2021'.
    API documentation
      http://contratacionesabiertas-iaipoaxaca-org.mx:4000/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_oaxaca_iaipo'

    # BaseSpider
    default_from_date = '2021'
    default_until_date = '2021'

    # PeriodicSpider
    pattern = 'http://contratacionesabiertas-iaipoaxaca-org.mx:3000/edca/contractingprocess/{}'
