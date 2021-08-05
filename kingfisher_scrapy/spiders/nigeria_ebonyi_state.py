from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components


class NigeriaEbonyiState(PeriodicSpider):
    """
    Domain
      Ebonyi E-PROCUREMENT
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2018'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    Bulk download documentation
      https://ebonyieprocure.eb.gov.ng/ocds_report.php
    """
    name = 'nigeria_ebonyi_state'

    # BaseSpider
    date_format = 'year'
    default_from_date = '2018'

    # PeriodicSpider
    pattern = 'http://ebonyieprocure.eb.gov.ng/media/ocds{}.json'

    # SimpleSpider
    data_type = 'release_package'

    def get_formatter(self):
        return components(-1)
