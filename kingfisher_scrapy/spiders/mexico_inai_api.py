from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components


class MexicoINAIAAPI(PeriodicSpider):
    """
    Domain
      Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales (INAI)
    Spider arguments
      from_date
        Download only releases from this date onward (YYYY format).
        If ``from_date`` is not provided defaults to 2015.
      until_date
        Download only releases until this date (YYYY format).
        If ``from_date`` is not provided defaults to current year.
    API documentation
      http://contratacionesabiertas.inai.org.mx/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_inai_api'

    # BaseSpider
    root_path = 'arrayReleasePackage.item'
    date_format = 'year'
    default_from_date = '2015'

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = 'http://contratacionesabiertas.inai.org.mx:3000/edca/contractingprocess/{}'

    def get_formatter(self):
        return components(-1)
