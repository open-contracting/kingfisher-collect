from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import browser_user_agent, parameters


class MexicoNuevoLeonRecords(PeriodicSpider):
    """
    Domain
      Secretaría de Movilidad y Planeación Urbana de Nuevo León
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2013'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    Bulk download documentation
      https://smpu.nl.gob.mx/transparencia/publicaciones
    """

    name = 'mexico_nuevo_leon_records'
    user_agent = browser_user_agent  # to avoid HTTP 403

    # SimpleSpider
    data_type = 'record_package'

    # PeriodicSpider
    date_format = 'year'
    pattern = 'https://smpu.nl.gob.mx/siasi_ws/api/ocds/ListarProduccionXAnio?anio=%5B%7B"value":"{0}"%7D%5D'
    formatter = staticmethod(parameters('anio'))
    default_from_date = '2013'
