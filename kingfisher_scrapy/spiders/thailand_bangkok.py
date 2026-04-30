from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import components


class ThailandBangkok(PeriodicSpider):
    """
    Domain
      Bangkok Metropolitan Administration (BMA)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2023'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    Bulk download documentation
      https://opencontract.bangkok.go.th/ocds.html
    """

    name = "thailand_bangkok"

    # BaseSpider
    date_format = "year"
    default_from_date = "2023"

    # SimpleSpider
    data_type = "release_package"

    # PeriodicSpider
    pattern = "https://opencontract.bangkok.go.th/assets/data/output/yearly/ocds_releases_{}.json"
    formatter = staticmethod(components(-1))

    def build_urls(self, year):
        # Yearly files use the Buddhist calendar year (Gregorian + 543).
        yield self.pattern.format(year + 543)
