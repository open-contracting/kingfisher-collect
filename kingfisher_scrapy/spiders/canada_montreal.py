import json

import scrapy


class CanadaMontreal(scrapy.Spider):
    name = 'canada_montreal'
    start_urls = ['https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit=1']

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        total = data['meta']['count']
        offset = 0
        limit = 10000
        if hasattr(self, 'sample') and self.sample == 'true':
            total = 1
            limit = 50
        while offset < total:
            yield {
                'file_urls': ['https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit=%d&offset=%d' %
                              (limit, offset)],
                'data_type': 'release_package',
            }
            offset += limit
