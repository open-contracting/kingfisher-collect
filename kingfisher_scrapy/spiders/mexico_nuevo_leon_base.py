from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import browser_user_agent, parameters


class MexicoNuevoLeonBase(PeriodicSpider):
    user_agent = browser_user_agent  # to avoid HTTP 403

    # BaseSpider
    date_format = 'year'
    default_from_date = '2013'

    # PeriodicSpider
    pattern = 'https://smpu.nl.gob.mx/siasi_ws/api/ocds/ListarProduccionXAnio?anio=%5B%7B"value":"{0}"%7D%5D'
    formatter = staticmethod(parameters('anio'))
