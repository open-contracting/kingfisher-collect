import json
from json import JSONDecodeError

import scrapy
import time

from kingfisher_scrapy.base_spider import BaseSpider


# This Spider uses the old system of pipelines! DO NOT USE IT AS AN EXAMPLE OF WHAT TO DO IN FUTURE SPIDERS!
# Thank you.
class Colombia(BaseSpider):
    name = 'colombia'
    start_urls = ['https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/rest/releases?page=1']
    handle_httpstatus_list = [503]
    sleep = 120 * 60
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.OldKingfisherFilesPipeline': 400,
            'kingfisher_scrapy.pipelines.OldKingfisherPostPipeline': 800,
        }
    }

    def start_requests(self):
        base_url = 'https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/rest/releases?page=%d'
        start_page = 1
        if hasattr(self, 'page'):
            start_page = int(self.page)
        yield scrapy.Request(url=base_url % start_page, callback=self.parse)

    def parse(self, response):
        # In Colombia, every day at certain hour they run a process in their system that drops the database and make
        # the services unavailable for about 120 minutes, as Colombia has a lot of data,
        # the spider takes more than one day to scrape all the data,
        # so eventually the spider will always face the service problems. For that, when the problem occurs, (503
        # status or invalid json) we wait 120 minutes and then continue
        try:

            if response.status == 503:
                time.sleep(self.sleep)
                yield scrapy.Request(response.url)
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
            time.sleep(self.sleep)
            yield scrapy.Request(response.url)
