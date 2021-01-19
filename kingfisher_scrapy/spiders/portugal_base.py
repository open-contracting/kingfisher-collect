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
    max_number_of_retries = 15
    wait_time = 180

    def start_requests(self):
        url = self.url
        if self.from_date and self.until_date:
            url = f'{url}&contractStartDate={self.from_date}&contractEndDate={self.until_date}'
        yield scrapy.Request(url, meta={'file_name': 'offset-1.json'})

    def parse(self, response):
        # after a undefined number of requests (around 36100?), the API returns 5XX errors.
        # After waiting a few seconds the URL works again
        if not self.is_http_success(response):
            if self.number_of_retries < self.max_number_of_retries:
                self.logger.info(f'Response status {response.status} waiting {self.wait_time} '
                                 f'seconds before continue, attempt {self.number_of_retries}')
                yield self.build_file_error_from_response(response)
                time.sleep(self.wait_time)
                self.number_of_retries = self.number_of_retries + 1
                # if it fails again for the same request, we wait more
                self.wait_time = self.wait_time * self.number_of_retries
                yield scrapy.Request(response.request.url, dont_filter=True, meta=response.request.meta)
            else:
                self.logger.info(f'Response status {response.status}, maximum attempts reached, giving up')
                yield self.build_file_error_from_response(response)
        else:
            self.number_of_retries = 0
            self.wait_time = 180
            yield from super().parse(response)
