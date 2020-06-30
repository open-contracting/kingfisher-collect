from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, date_range_by_year


class MoldovaOld(SimpleSpider):
    """
    Bulk download documentation
      http://opencontracting.date.gov.md/downloads
    Spider arguments
      sample
        Downloads a single JSON file containing data for 2017.
    """
    name = 'moldova_old'
    data_type = 'release_package'

    def start_requests(self):
        pattern = 'http://opencontracting.date.gov.md/ocds-api/year/{}'

        start = 2012
        stop = 2018
        if self.sample:
            start = 2018

        for year in date_range_by_year(start, stop):
            yield self.build_request(pattern.format(year), formatter=components(-1))
