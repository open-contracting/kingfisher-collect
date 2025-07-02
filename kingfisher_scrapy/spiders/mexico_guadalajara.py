from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.spiders.mexico_inai_base import MexicoINAIBase
from kingfisher_scrapy.util import components


class MexicoGuadalajara(PeriodicSpider, MexicoINAIBase):
    """
    Domain
      Municipio de Guadalajara
    Caveats
      The API documentation suggests they have data only for 2022, but they have it up to the current year as well.
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2022'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    API documentation
      https://contratacionesabiertas.guadalajara.gob.mx:4000/contratacionesabiertas/datosabiertos
    """

    name = "mexico_guadalajara"

    # BaseSpider
    default_from_date = "2022"

    # MexicoINAIBase
    base_url = "https://contratacionesabiertas.guadalajara.gob.mx:3000"

    # PeriodicSpider
    formatter = staticmethod(components(-1))
    pattern = "https://contratacionesabiertas.guadalajara.gob.mx:3000/edca/contractingprocess/{0}"
