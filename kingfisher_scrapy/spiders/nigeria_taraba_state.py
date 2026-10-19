from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import components


class NigeriaTarabaState(PeriodicSpider):
    """
    Domain
      Taraba State Bureau of Public Procurement
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2024'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    API documentation
      https://procurement.tarabastate.gov.ng/api/ocds
    """

    name = "nigeria_taraba_state"

    # BaseSpider
    date_format = "year"
    default_from_date = "2024"

    # SimpleSpider
    data_type = "release_package"

    # PeriodicSpider
    pattern = "https://procurement.tarabastate.gov.ng/api/ocds/packages/{}"
    formatter = staticmethod(components(-1))
