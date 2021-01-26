import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class PortugalBase(LinksSpider):
    default_from_date = '2010-01-01'
    next_page_formatter = staticmethod(parameters('offset'))
    # The API otherwise returns HTTP 429.
    download_delay = 1

    # We will wait 1, 2, 4, 8, 16 minutes (31 minutes total).
    max_retries = 6
    initial_wait_time = 30

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'kingfisher_scrapy.middlewares.DelayedRequestsMiddleware': 543,
        }
    }

    def start_requests(self):
        url = self.url
        if self.from_date and self.until_date:
            url = f'{url}&contractStartDate={self.from_date}&contractEndDate={self.until_date}'

        yield scrapy.Request(url, meta={'file_name': 'offset-1.json'})

    def parse(self, response):

        retries = response.request.meta.get('retries', 0)
        wait_time = response.request.meta.get('delay_request', self.initial_wait_time)

        # Every ~36,000 requests, the API returns HTTP errors. After a few minutes, it starts working again.
        # https://github.com/open-contracting/kingfisher-collect/issues/545#issuecomment-762768460
        if self.is_http_success(response):
            yield from super().parse(response)
        elif retries < self.max_retries:
            response.request.meta['retries'] = retries + 1
            response.request.meta['delay_request'] = wait_time * 2
            request = scrapy.Request(response.request.url, meta=response.request.meta, dont_filter=True)

            self.logger.debug('Retrying %(request)s in %(wait_time)ds (failed %(retries)d times): HTTP %(status)d',
                              {'request': response.request, 'retries': response.request.meta['retries'],
                               'status': response.status, 'wait_time': response.request.meta['delay_request']},
                              extra={'spider': self})

            yield request
        else:
            self.logger.error('Gave up retrying %(request)s (failed %(retries)d times): HTTP %(status)d',
                              {'request': response.request, 'retries': retries, 'status': response.status},
                              extra={'spider': self})
            yield self.build_file_error_from_response(response)
