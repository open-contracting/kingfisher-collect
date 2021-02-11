from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components


class MoldovaOld(PeriodicSpider):
    """
    Domain
      Public Procurement Agency (PPA)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY format). Defaults to '2012'.
      until_date
        Download only data until this month (YYYY format). Defaults to '2018'.
    Bulk download documentation
      http://opencontracting.date.gov.md/downloads
    """
    name = 'moldova_old'

    # BaseSpider
    date_format = 'year'
    default_from_date = '2012'
    default_until_date = '2018'

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = 'http://opencontracting.date.gov.md/ocds-api/year/{}'

    def get_formatter(self):
        return components(-1)
