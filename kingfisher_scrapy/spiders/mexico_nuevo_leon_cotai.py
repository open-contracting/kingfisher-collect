from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoNuevoLeonCOTAI(MexicoINAIBase):
    """
    Domain
      Comisión de Transparencia y Acceso a la Información del Estado de Nuevo León (COTAI)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2020'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2020'.
    API documentation
      http://201.149.38.218:4000/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_nuevo_leon_cotai'

    # BaseSpider
    default_from_date = '2020'
    default_until_date = '2020'

    # PeriodicSpider
    pattern = 'http://201.149.38.218:3000/edca/contractingprocess/{}'
