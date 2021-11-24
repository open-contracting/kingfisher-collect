from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components


class ItalyANAC(PeriodicSpider):
    """
    Domain
       Italy ANAC
    Bulk download documentation
      https://dati.anticorruzione.it/opendata/organization/anticorruzione
    """
    name = 'italy_anac'
    download_timeout = 99999

    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2018-01'
    default_until_date = '2020-12'

    # PeriodicSpider
    pattern = 'https://dati.anticorruzione.it/' \
              'opendata/download/dataset/ocds/filesystem/bulk/{0.year:d}/{0.month:02d}.json'
    formatter = staticmethod(components(-1))

    # SimpleSpider
    data_type = 'release_package'
