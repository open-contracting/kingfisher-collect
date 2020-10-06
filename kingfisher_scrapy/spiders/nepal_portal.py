from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components


class NepalPortal(PeriodicSpider):
    """
    Bulk download documentation
      http://ppip.gov.np/downloads
    Spider arguments
      sample
        Download only data released on 2018.
    """
    name = 'nepal_portal'
    data_type = 'release_package'
    ocds_version = '1.0'
    default_from_date = '2012'
    default_until_date = '2018'  # HTTP 500 after 2018
    pattern = 'http://ppip.gov.np/bulk-download/{}'
    date_format = 'year'

    def get_formatter(self):
        return components(-1)
