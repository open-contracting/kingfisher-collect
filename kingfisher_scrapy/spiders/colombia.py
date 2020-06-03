import hashlib
import logging
import time
from datetime import datetime
from json import JSONDecodeError

import scrapy

from kingfisher_scrapy.base_spider import LinksSpider


class Colombia(LinksSpider):
    name = 'colombia'
    sleep = 120 * 60
    start_year = 2011

    def get_year_until(self):
        until_year = datetime.now().year + 1
        if hasattr(self, 'year'):
            self.start_year = int(self.year)
            until_year = self.start_year + 1
        return until_year

    def start_requests(self):
        base_url = 'https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/rest/releases/page/{}'
        base_url += '?page={}'
        start_page = 1
        if hasattr(self, 'page'):
            start_page = int(self.page)
        until_year = self.get_year_until()
        for year in reversed(range(self.start_year, until_year)):
            yield scrapy.Request(base_url.format(year, start_page), meta={'kf_filename': 'page{}.json'.format(start_page)})

    def parse(self, response):
        # In Colombia, every day at certain hour they run a process in their system that drops the database and make
        # the services unavailable for about 120 minutes, as Colombia has a lot of data,
        # the spider takes more than one day to scrape all the data,
        # so eventually the spider will always face the service problems. For that, when the problem occurs, (503
        # status or invalid json) we wait 120 minutes and then continue
        try:
            if response.status == 503 or response.status == 404:
                url = response.request.url
                logging.info('Sleeping due error {} in url {}'.format(response.status, url))
                time.sleep(self.sleep)
                yield scrapy.Request(
                    url,
                    dont_filter=True,
                    meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
                )
            elif self.is_http_success(response):
                yield self.build_file_from_response(response, data_type='release_package')
                if not self.sample:
                    yield self.next_link(response)
            else:
                yield self.build_file_error_from_response(response)

        except JSONDecodeError:
            url = response.request.url
            logging.info('Sleeping due json decode error in url {}'.format(url))
            time.sleep(self.sleep)
            yield scrapy.Request(url, dont_filter=True,
                                 meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'})
