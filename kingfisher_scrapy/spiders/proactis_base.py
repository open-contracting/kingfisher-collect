from datetime import date

from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class ProactisBase(PeriodicSpider):
    # BaseSpider
    date_format = 'year-month'
    default_from_date = date(date.today().year - 1, date.today().month, 1)

    # PeriodicSpider
    pattern = '/v1/Notices?dateFrom={:%m-%Y}&outputType=0&noticeType={}'
    formatter = staticmethod(parameters('noticeType', 'dateFrom'))

    # url_base and notice_types must be provided by subclasses.

    def build_urls(self, date):
        url = self.url_base + self.pattern
        for notice_type in self.notice_types:
            yield url.format(date, notice_type)

    @handle_http_error
    def parse(self, response):
        data = response.json()
        # Some responses are a package without a list of releases.
        if 'releases' not in data:
            yield self.build_file_error_from_response(response, errors=data)
        else:
            yield from super().parse(response)
