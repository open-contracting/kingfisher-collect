import json

from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import BROWSER_USER_AGENT, parameters


def parser(value):
    # The 'anio' query string parameter looks like [{"value":"2024"}] (before URL encoding).
    return json.loads(value)[0]["value"]


class MexicoNuevoLeonBase(PeriodicSpider):
    custom_settings = {
        "USER_AGENT": BROWSER_USER_AGENT,  # to avoid HTTP 403
    }

    # BaseSpider
    date_format = "year"
    default_from_date = "2013"

    # PeriodicSpider
    pattern = 'https://smpu.nl.gob.mx/siasi_ws/api/ocds/ListarProduccionXAnio?anio=%5B%7B"value":"{0}"%7D%5D'
    formatter = staticmethod(parameters("anio", parser=parser))
