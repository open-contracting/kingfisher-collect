from kingfisher_scrapy.base_spider import PeriodicalSpider
from kingfisher_scrapy.util import components


class NepalPortal(PeriodicalSpider):
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
    start = 2012
    stop = 2018
    pattern = 'http://ppip.gov.np/bulk-download/{}'
    date_format = 'year'

    def get_formatter(self):
        return components(-1)
