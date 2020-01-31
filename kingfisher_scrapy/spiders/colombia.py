import hashlib
import json
import logging
import time
from json import JSONDecodeError

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class Colombia(BaseSpider):
    name = 'colombia'
    sleep = 120 * 60

    def start_requests(self):
        base_url = 'https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/rest/releases?page=%d'
        if hasattr(self, 'year'):
            year = int(self.year)
            base_url = 'https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/rest/releases/page/{}?page=%d'.format(year)
        start_page = 1
        if hasattr(self, 'page'):
            start_page = int(self.page)
        yield scrapy.Request(
            url=base_url % start_page,
            meta={'kf_filename': 'page{}.json'.format(start_page)}
        )

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
                yield scrapy.Request(url,
                                     dont_filter=True,
                                     meta={'kf_filename': hashlib.md5(
                                         url.encode('utf-8')).hexdigest() + '.json'})

            elif response.status == 200:

                yield self.save_response_to_disk(response, response.request.meta['kf_filename'],
                                                 data_type='release_package')

                json_data = json.loads(response.body_as_unicode())
                if not self.is_sample():
                    if 'links' in json_data and 'next' in json_data['links']:
                        url = json_data['links']['next']
                        yield scrapy.Request(
                            url=url,
                            meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
                        )

            else:

                yield {
                    'success': False,
                    'file_name': response.request.meta['kf_filename'],
                    'url': response.request.url,
                    'errors': {'http_code': response.status}
                }

        except JSONDecodeError:
            url = response.request.url
            logging.info('Sleeping due json decode error in url {}'.format(url))
            time.sleep(self.sleep)
            yield scrapy.Request(url, dont_filter=True,
                                 meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'})
