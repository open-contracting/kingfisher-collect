import logging
import time
from json import JSONDecodeError

import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class Colombia(LinksSpider):
    """
    API documentation
      https://www.colombiacompra.gov.co/transparencia/api
    Swagger API documentation
      https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/
    Spider arguments
      sample
        Download only the first page of results.
      page
        The page number from which to start crawling.
      year
        The year to crawl. See API documentation for valid values.
      from_date
        Download only releases from this release.date onward (YYYY-MM-DD format).
        If `until_date` is provided and ``from_date`` don't, defaults to '2011-01-01'.
      until_date
        Download only releases until this release.date (YYYY-MM-DD format).
        If ``from_date`` is provided and ``until_date`` don't, defaults to today.
    """
    name = 'colombia'
    next_page_formatter = staticmethod(parameters('_id'))
    default_from_date = '2011-01-01'

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        if (spider.from_date or spider.until_date) and hasattr(spider, 'year'):
            raise scrapy.exceptions.CloseSpider('You cannot specify both a year spider argument and '
                                                'from_date/until_date spider argument(s).')
        return spider

    def start_requests(self):
        base_url = 'https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/rest/releases'
        if hasattr(self, 'year'):
            base_url += f'/page/{int(self.year)}'
        elif self.from_date or self.until_date:
            from_date = self.from_date.strftime(self.date_format)
            until_date = self.until_date.strftime(self.date_format)
            base_url += f'/dates/{from_date}/{until_date}'

        base_url += '?page={}'

        page = 1
        if hasattr(self, 'page'):
            page = int(self.page)
        yield self.build_request(base_url.format(page), formatter=parameters('page'))

    def retry(self, response, reason):
        url = response.request.url
        logging.info(reason.format(url=url, status=response.status))
        time.sleep(120 * 60)
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
            elif response.status == 503:
                self.retry(response, 'Sleeping due to HTTP error {status} from {url}')
            else:
                yield self.build_file_error_from_response(response)
        except JSONDecodeError:
            self.retry(response, 'Sleeping due to JSONDecodeError from {url}')
