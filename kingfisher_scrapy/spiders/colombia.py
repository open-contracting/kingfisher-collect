import json
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class Colombia(BaseSpider):
    name = 'colombia'
    start_urls = ['https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/rest/releases?page=1']

    def parse(self, response):
        json_data = json.loads(response.body_as_unicode())
        if not (hasattr(self, 'sample') and self.sample == 'true'):
            if 'links' in json_data and 'next' in json_data['links']:
                yield scrapy.Request(json_data['links']['next'])

        yield {
            'file_urls': [response.url],
            'data_type': 'release_package'
        }
