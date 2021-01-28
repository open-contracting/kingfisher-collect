import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class PortugalBase(LinksSpider):
    default_from_date = '2010-01-01'
    next_page_formatter = staticmethod(parameters('offset'))

    # We will wait 1, 2, 4, 8, 16 minutes (31 minutes total).
    max_retries = 5
    half_initial_wait_time = 30

    def start_requests(self):
        url = self.url
        if self.from_date and self.until_date:
            url = f'{url}&contractStartDate={self.from_date}&contractEndDate={self.until_date}'

        yield scrapy.Request(url, meta={'file_name': 'offset-1.json'})

    # https://github.com/scrapy/scrapy/blob/master/scrapy/downloadermiddlewares/retry.py
    def parse(self, response):
        retries = response.request.meta.get('retries', 0) + 1
        wait_time = response.request.meta.get('wait_time', self.half_initial_wait_time) * 2

        # Every ~36,000 requests, the API returns HTTP errors. After a few minutes, it starts working again.
        # The number of failed attempts in the log messages includes the original request.
        # https://github.com/open-contracting/kingfisher-collect/issues/545#issuecomment-762768460
        if self.is_http_success(response):
            yield from super().parse(response)
        elif retries <= self.max_retries:
            request = response.request.copy()
            request.meta['retries'] = retries
            request.meta['wait_time'] = wait_time
            request.dont_filter = True

            self.logger.debug('Retrying %(request)s in %(wait_time)ds (failed %(failures)d times): HTTP %(status)d',
                              {'request': response.request, 'failures': retries, 'status': response.status,
                               'wait_time': wait_time},
                              extra={'spider': self})

            yield request
        else:
            self.logger.error('Gave up retrying %(request)s (failed %(failures)d times): HTTP %(status)d',
                              {'request': response.request, 'failures': retries, 'status': response.status},
                              extra={'spider': self})

            yield self.build_file_error_from_response(response)
