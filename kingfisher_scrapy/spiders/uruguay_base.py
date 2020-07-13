from datetime import date

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, date_range_by_month


class UruguayBase(SimpleSpider):
    download_delay = 0.9
    default_from_date = '2017-11'

    @classmethod
    def from_crawler(cls, crawler, sample=None, from_date=None, until_date=None, *args, **kwargs):
        if not from_date:
            from_date = cls.default_from_date
        if not until_date:
            until_date = date.today().strftime('%Y-%m')
        if sample:
            from_date = until_date

        return super().from_crawler(crawler, date_format='year-month', sample=sample, from_date=from_date,
                                    until_date=until_date, *args, **kwargs)

    def start_requests(self):
        url = 'http://comprasestatales.gub.uy/ocds/rss/{0.year:d}/{0.month:02d}'

        for d in date_range_by_month(self.from_date, self.until_date):
            yield self.build_request(url.format(d), formatter=components(-2), callback=self.parse_list)
