from datetime import date, datetime

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, date_range_by_month


class UruguayBase(SimpleSpider):
    download_delay = 0.9
    default_from_date = '11-2017'

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        return super(UruguayBase, cls).from_crawler(crawler, date_format='month-year', *args, **kwargs)

    def start_requests(self):
        url = 'http://comprasestatales.gub.uy/ocds/rss/{0.year:d}/{0.month:02d}'
        start = self.from_date if self.from_date else datetime.strptime(self.default_from_date, self.date_format)
        stop = self.until_date if self.until_date else date.today().replace(day=1)
        if self.sample:
            start = stop

        for d in date_range_by_month(start, stop):
            yield self.build_request(url.format(d), formatter=components(-2), callback=self.parse_list)
