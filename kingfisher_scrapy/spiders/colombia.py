import json
from json import JSONDecodeError

import scrapy
import time

from kingfisher_scrapy.base_spider import BaseSpider


def wait_and_retry(url):
    time.sleep(120 * 60)
    yield scrapy.Request(url)


class Colombia(BaseSpider):
    name = 'colombia'
    start_urls = ['https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/rest/releases?page=1']
    handle_httpstatus_list = [503]

    def parse(self, response):
        # In Colombia, every day at certain hour they run a process in their system that drops the database and make
        # the services unavailable for about 120 minutes, as Colombia has a lot of data,
        # the spider takes more than one day to scrape all the data,
        # so eventually the spider will always face the service problems. For that, when the problem occurs, (503
        # status or invalid json) we wait 120 minutes and then continue
        try:

            if response.status == 503:
                wait_and_retry(response.url)
            else:
                json_data = json.loads(response.body_as_unicode())
                if not self.is_sample():
                    if 'links' in json_data and 'next' in json_data['links']:
                        yield scrapy.Request(json_data['links']['next'])

                yield {
                    'file_urls': [response.url],
                    'data_type': 'release_package'
                }

        except JSONDecodeError:
            wait_and_retry(response.url)
