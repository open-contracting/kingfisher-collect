from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components


class MoldovaOld(PeriodicSpider):
    """
    Domain
      Public Procurement Agency (PPA)
    Bulk download documentation
      http://opencontracting.date.gov.md/downloads
    """
    name = 'moldova_old'
    data_type = 'release_package'

    # PeriodicSpider variables
    date_format = 'year'
    default_from_date = '2012'
    default_until_date = '2018'
    pattern = 'http://opencontracting.date.gov.md/ocds-api/year/{}'

    def get_formatter(self):
        return components(-1)
