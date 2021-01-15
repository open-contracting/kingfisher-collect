from kingfisher_scrapy.base_spider import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.util import components


class Zambia(CompressedFileSpider, PeriodicSpider):
    """
    Domain
      Zambia Public Procurement Authority
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2016-07'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    """
    name = 'zambia'
    data_type = 'record_package'
    ocds_version = '1.0'

    # PeriodicSpider variables
    date_format = 'year-month'
    default_from_date = '2016-07'
    pattern = 'https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackage/{0.year:d}/{0.month:02d}'

    def get_formatter(self):
        return components(-2)
