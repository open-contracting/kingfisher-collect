from abc import abstractmethod

from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import components


class UruguayBase(PeriodicSpider):
    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2017-11'

    # PeriodicSpider
    pattern = 'http://comprasestatales.gub.uy/ocds/rss/{0:%Y}/{0:%m}'
    formatter = staticmethod(components(-2))  # year-month
    start_requests_callback = 'parse_list'

    @abstractmethod
    def parse_list(self, response):
        pass
