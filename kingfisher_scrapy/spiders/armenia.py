import json

import scrapy


class Armenia(scrapy.Spider):
    name = 'armenia'
    start_urls = ['https://armeps.am/ocds/release']

    def parse(self, response):
        json_data = json.loads(response.body_as_unicode())
        if not (hasattr(self, 'sample') and self.sample == 'true'):
            if 'next_page' in json_data and 'uri' in json_data['next_page']:
                yield scrapy.Request(json_data['next_page']['uri'])

        yield {
            'file_urls': [response.url],
            'data_type': 'release_package'
        }
