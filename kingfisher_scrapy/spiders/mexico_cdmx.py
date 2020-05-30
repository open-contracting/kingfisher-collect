import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class MexicoCDMXSource(BaseSpider):
    name = 'mexico_cdmx'

    def start_requests(self):
        yield scrapy.Request(
            'http://www.contratosabiertos.cdmx.gob.mx/api/contratos/todos',
            meta={'kf_filename': 'list.json'},
            callback=self.parse_list
        )

    @handle_error
    def parse_list(self, response):
        data = json.loads(response.text)
        if self.sample:
            data = [data[0]]

        for data_item in data:
            yield scrapy.Request(
                data_item['uri'],
                meta={'kf_filename': 'id%s.json' % data_item['id']},
                callback=self.parse_record
            )

    @handle_error
    def parse_record(self, response):
        yield self.build_file_from_response(response, data_type='release_package')
