from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, date_range_by_month


class UruguayBase(SimpleSpider):
    download_delay = 0.9
    default_from_date = '2017-11'

    @classmethod
    def from_crawler(cls, crawler, from_date=None, *args, **kwargs):
        if not from_date:
            from_date = cls.default_from_date

        return super().from_crawler(crawler, date_format='year-month', from_date=from_date, *args, **kwargs)

    def start_requests(self):
        url = 'http://comprasestatales.gub.uy/ocds/rss/{0.year:d}/{0.month:02d}'
        if self.sample:
            self.from_date = self.until_date

        for d in date_range_by_month(self.from_date, self.until_date):
            yield self.build_request(url.format(d), formatter=components(-2), callback=self.parse_list)
