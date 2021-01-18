import time

import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class PortugalBase(LinksSpider):
    default_from_date = '2010-01-01'
    next_page_formatter = staticmethod(parameters('offset'))
    # The API return 429 error after a certain number of requests
    download_delay = 1
    # The API returns 503 error sometimes
    custom_settings = {
        'RETRY_TIMES': 10,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.5,
        'HTTPERROR_ALLOW_ALL': True
    }

    number_of_retries = 0

    def start_requests(self):
        url = self.url
        if self.from_date and self.until_date:
            url = f'{url}&contractStartDate={self.from_date}&contractEndDate={self.until_date}'
        yield scrapy.Request(url, meta={'file_name': 'offset-1.json'})

    def parse(self, response):
        # after a undefined number of requests, the API returns 5XX errors. After waiting a few seconds the URL
        # works again
        if not self.is_http_success(response):
            if self.number_of_retries < 5:
                self.logger.info(f'Response status {response.status} waiting 180 seconds before continue, '
                                 f'attempt {self.number_of_retries}')
                time.sleep(180)
                self.number_of_retries = self.number_of_retries + 1
                yield scrapy.Request(response.request.url, dont_filter=True, meta=response.request.meta)
            else:
                self.logger.info(f'Response status {response.status}, maximum attempts reached, giving up')
                yield self.build_file_error_from_response(response)
        else:
            yield from super().parse(response)
