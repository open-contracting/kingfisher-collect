from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase


class MexicoGuanajuatoIACIP(MexicoINAIBase):
    """
    Domain
      Instituto de Acceso a la Información Pública para el Estado de Guanajuato (IACIP)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2021'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    API documentation
      http://contratacionesabiertas.iacipgto.mx:4000/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_guanajuato_iacip'
    domain_pattern = 'http://162.214.71.135:3000/{}'

    # BaseSpider
    default_from_date = '2021'
