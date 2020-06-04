from datetime import date

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, date_range_by_month


class UruguayBase(SimpleSpider):
    download_delay = 0.9

    def start_requests(self):
        url = 'http://comprasestatales.gub.uy/ocds/rss/{0.year:d}/{0.month:02d}'

        start = date(2017, 11, 1)
        stop = date.today().replace(day=1)
        if self.sample:
            start = stop

        for d in date_range_by_month(start, stop):
            yield self.build_request(url.format(d), formatter=components(-2), callback=self.parse_list)
