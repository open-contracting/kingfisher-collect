from kingfisher_scrapy.base_spider import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.util import components


class Malta(CompressedFileSpider, PeriodicSpider):
    """
    Domain
      Malta
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2019-10'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    API documentation
      https://docs.google.com/document/d/1VnCEywKkkQ7BcVbT7HlW2s_N_QI8W0KE/edit
    """
    name = 'malta'
    data_type = 'record_package'

    # PeriodicSpider variables
    date_format = 'year-month'
    default_from_date = '2019-10'
    pattern = 'http://demowww.etenders.gov.mt/ocds/services/recordpackage/getrecordpackage/{0.year:d}/{0.month:02d}'

    def get_formatter(self):
        return components(-2)
