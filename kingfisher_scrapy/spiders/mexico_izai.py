from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components


class MexicoIZAI(PeriodicSpider):
    """
    Domain
      Instituto Zacatecano de Transparencia y Acceso a la Información (IZAI)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2016'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2021'.
    API documentation
      https://contratacionesabiertas.izai.org.mx/contratacionesabiertas/datosabiertos
    """
    name = 'mexico_izai'

    # BaseSpider
    root_path = 'arrayReleasePackage.item'
    date_format = 'year'
    default_from_date = '2016'
    default_until_date = '2021'

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = 'http://128.199.8.41:3000/edca/contractingprocess/{}'

    def get_formatter(self):
        return components(-1)
