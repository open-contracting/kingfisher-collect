import scrapy
from scrapy import signals
from scrapy.exceptions import DontCloseSpider
from twisted.internet import defer, reactor

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class PortugalBase(LinksSpider):
    default_from_date = '2010-01-01'
    next_page_formatter = staticmethod(parameters('offset'))
    # The API otherwise returns HTTP 429.
    download_delay = 1

    # We will wait 1, 2, 4, 8, 16 minutes (31 minutes total).
    retries = 0
    max_retries = 5
    wait_time = initial_wait_time = 60

    # https://stackoverflow.com/questions/46698333/deferred-requests-in-scrapy
    @classmethod
    def from_crawler(cls, crawler, **kwargs):
        spider = super().from_crawler(crawler, **kwargs)
        crawler.signals.connect(spider.spider_idle, signal=signals.spider_idle)
        return spider

    @classmethod
    def spider_idle(cls, spider):
        raise DontCloseSpider()

    def start_requests(self):
        url = self.url
        if self.from_date and self.until_date:
            url = f'{url}&contractStartDate={self.from_date}&contractEndDate={self.until_date}'

        yield scrapy.Request(url, meta={'file_name': 'offset-1.json'})

    def parse(self, response):
        # Every ~36,000 requests, the API returns HTTP errors. After a few minutes, it starts working again.
        # https://github.com/open-contracting/kingfisher-collect/issues/545#issuecomment-762768460
        if self.is_http_success(response):
            yield from super().parse(response)
        elif self.retries < self.max_retries:
            request = scrapy.Request(response.request.url, meta=response.request.meta, dont_filter=True)

            self.logger.debug('Retrying %(request)s in %(wait_time)ds (failed %(retries)d times): HTTP %(status)d',
                              {'request': response.request, 'retries': self.retries, 'status': response.status,
                               'wait_time': self.wait_time}, extra={'spider': self})
            deferred = defer.Deferred()
            reactor.callLater(self.wait_time, self.crawler.engine.schedule, request, spider=self)

            self.retries += 1
            self.wait_time *= 2

            return deferred
        else:
            self.logger.error('Gave up retrying %(request)s (failed %(retries)d times): HTTP %(status)d',
                              {'request': response.request, 'retries': self.retries, 'status': response.status},
                              extra={'spider': self})
            yield self.build_file_error_from_response(response)

        self.retries = 0
        self.wait_time = self.initial_wait_time
