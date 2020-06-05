from datetime import date

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, date_range_by_year


class NepalPortal(SimpleSpider):
    """
    Bulk download documentation
      http://ppip.gov.np/downloads
    Spider arguments
      sample
        Download only data released on 2018.
    """
    name = 'nepal_portal'
    data_type = 'release_package'

    def start_requests(self):
        pattern = 'http://ppip.gov.np/bulk-download/{}'

        if self.sample:
            start = 2018
            stop = 2018
        else:
            start = 2012
            stop = date.today().year  # HTTP 500 after 2018

        for year in date_range_by_year(start, stop):
            yield self.build_request(pattern.format(year), formatter=components(-1))
