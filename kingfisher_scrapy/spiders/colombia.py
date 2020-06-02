import logging
import time
from json import JSONDecodeError

import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class Colombia(LinksSpider):
    name = 'colombia'
    sleep = 120 * 60
    next_page_formatter = parameters('page')

    def start_requests(self):
        base_url = 'https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/rest/releases'
        if hasattr(self, 'year'):
            base_url += f'/page/{int(self.year)}'
        base_url += '?page={}'

        page = 1
        if hasattr(self, 'page'):
            page = int(self.page)
        yield self.build_request(base_url.format(page), formatter=parameters('page'))

    def retry(self, response, reason):
        url = response.request.url
        logging.info(reason.format(url=url, status=response.status))
        time.sleep(self.sleep)
        yield scrapy.Request(url, dont_filter=True, meta=response.request.meta)

    def parse(self, response):
        # In Colombia, every day at certain hour they run a process in their system that drops the database and make
        # the services unavailable for about 120 minutes, as Colombia has a lot of data,
        # the spider takes more than one day to scrape all the data,
        # so eventually the spider will always face the service problems. For that, when the problem occurs, (503
        # status or invalid json) we wait 120 minutes and then continue
        try:
            if self.is_http_success(response):
                yield self.build_file_from_response(response, data_type='release_package')
                if not self.sample:
                    yield self.next_link(response)
            elif response.status == 503 or response.status == 404:
                self.retry(response, 'Sleeping due to HTTP error {status} from {url}')
            else:
                yield self.build_file_error_from_response(response)
        except JSONDecodeError:
            self.retry(response, 'Sleeping due to JSONDecodeError from {url}')
