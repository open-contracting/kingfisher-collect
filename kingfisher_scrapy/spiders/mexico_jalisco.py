import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_error


class MexicoJalisco(SimpleSpider):
    name = 'mexico_jalisco'
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            'https://contratacionesabiertas.jalisco.gob.mx/OCApi/2017/contracts',
            meta={'kf_filename': 'list.json'},
            callback=self.parse_list
        )

    @handle_error
    def parse_list(self, response):
        items = json.loads(response.text)
        if self.sample:
            items = [items[0]]

        for item in items:
            yield scrapy.Request(
                item['URIContract'],
                meta={'kf_filename': f"id{item['ocid']}.json"},
                callback=self.parse_record_package
            )

    @handle_error
    def parse_record_package(self, response):
        yield self.build_file_from_response(response, data_type='record_package')

        data = json.loads(response.text)
        if 'packages' in data:
            for url in data['packages']:
                yield self.build_request(url, formatter=components(-1))
