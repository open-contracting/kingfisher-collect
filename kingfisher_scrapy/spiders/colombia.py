import json
from json import JSONDecodeError

import scrapy
import time

from kingfisher_scrapy.base_spider import BaseSpider


class Colombia(BaseSpider):
    name = 'colombia'
    start_urls = ['https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/rest/releases?page=1']

    def parse(self, response):
        try:
            json_data = json.loads(response.body_as_unicode())
            if not self.is_sample():
                if 'links' in json_data and 'next' in json_data['links']:
                    yield scrapy.Request(json_data['links']['next'])

            yield {
                'file_urls': [response.url],
                'data_type': 'release_package'
            }

        except JSONDecodeError:
            time.sleep(120*60)
            yield scrapy.Request(response.url)
