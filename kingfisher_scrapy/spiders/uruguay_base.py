from abc import abstractmethod

from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components


class UruguayBase(PeriodicSpider):
    download_delay = 0.9

    # PeriodicSpider variables
    date_format = 'year-month'
    default_from_date = '2017-11'
    pattern = 'http://comprasestatales.gub.uy/ocds/rss/{0.year:d}/{0.month:02d}'
    start_requests_callback = 'parse_list'

    def get_formatter(self):
        return components(-2)

    @abstractmethod
    def parse_list(self):
        pass
