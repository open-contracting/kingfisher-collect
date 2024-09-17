from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoVeracruzIVAI(MexicoINAIBase):
    """
    Domain
      Instituto Veracruzano de Acceso a la Información y Protección de Datos Personales
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2020'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      http://www.ivai.org.mx/contrataciones-abiertas/
    """

    name = 'mexico_veracruz_ivai'

    # BaseSpider
    default_from_date = '2020'

    # MexicoINAIBase
    base_url = 'http://187.216.225.247:3000'
