import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class PortugalBase(LinksSpider):
    # BaseSpider
    default_from_date = '2010-01-01'

    # LinksSpider
    formatter = staticmethod(parameters('offset'))

    # Local
    # We will wait 1, 2, 4, 8, 16 minutes (31 minutes total).
    max_retries = 5
    initial_wait_time = 60
    # start_url must be provided by subclasses.

    def start_requests(self):
        url = self.start_url
        if self.from_date and self.until_date:
            url = f'{url}?contractStartDate={self.from_date.strftime(self.date_format)}' \
                  f'&contractEndDate={self.until_date.strftime(self.date_format)}'

        yield scrapy.Request(url, meta={'file_name': 'offset-1.json'})

    # https://github.com/scrapy/scrapy/blob/master/scrapy/downloadermiddlewares/retry.py
    def parse(self, response):
        wait_time = response.request.meta.get('wait_time', self.initial_wait_time // 2) * 2

        # Every ~36,000 requests, the API returns HTTP errors. After a few minutes, it starts working again.
        # The number of failed attempts in the log messages includes the original request.
        # https://github.com/open-contracting/kingfisher-collect/issues/545#issuecomment-762768460
        if self.is_http_success(response) or response.status == 404:
            yield from super().parse(response)
        else:
            yield self.build_retry_request_or_file_error(response, wait_time, self.max_retries, True)
