from abc import abstractmethod

from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components, join, parameters


class NigeriaCrossRiverBase(PeriodicSpider):
    # SimpleSpider
    base_url = 'http://ocdsapi.dppib-crsgov.org/api/ocdsAPI/'

    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2020-02'
    default_until_date = '2020-11'

    def get_formatter(self):
        return join(components(-1), parameters('year', 'month'))

    @abstractmethod
    def build_urls(self, date):
        pass
