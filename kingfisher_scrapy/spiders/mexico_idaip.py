from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components


class MexicoIDAIP(PeriodicSpider):
    """
    Domain
      Instituto Duranguense de Acceso a la Información y de Protección de Datos Personales (IDAIP)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2020'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2021'.
    API documentation
      http://contratacionesabiertas.idaip.org.mx/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_idaip'

    # BaseSpider
    root_path = 'arrayReleasePackage.item'
    date_format = 'year'
    default_from_date = '2020'
    default_until_date = '2021'

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = 'http://74.208.135.52:3000/edca/contractingprocess/{}'

    def get_formatter(self):
        return components(-1)
