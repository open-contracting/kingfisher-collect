from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoNuevoLeonCOTAI(MexicoINAIBase):
    """
    Domain
      Comisión de Transparencia y Acceso a la Información del Estado de Nuevo León (COTAI)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2020'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      http://201.149.38.218:4000/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_nuevo_leon_cotai'
    domain_pattern = 'http://201.149.38.218:3000/{}'

    # BaseSpider
    default_from_date = '2020'
