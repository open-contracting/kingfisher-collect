import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class MexicoJalisco(BaseSpider):
    name = 'mexico_jalisco'

    def start_requests(self):
        yield scrapy.Request(
            'https://contratacionesabiertas.jalisco.gob.mx/OCApi/2017/contracts',
            meta={'kf_filename': 'list.json'},
            callback=self.parse_list
        )

    @handle_error
    def parse_list(self, response):
        datas = json.loads(response.text)
        if self.sample:
            datas = [datas[0]]
        for data in datas:
            yield scrapy.Request(
                data['URIContract'],
                meta={'kf_filename': 'id%s.json' % data['ocid']},
                callback=self.parse_record_package
            )

    @handle_error
    def parse_record_package(self, response):
        json_data = json.loads(response.text)
        if 'packages' in json_data:
            for url in json_data['packages']:
                yield scrapy.Request(
                    url,
                    meta={'kf_filename': 'packages-%s.json' % hashlib.md5(url.encode('utf-8')).hexdigest()},
                    callback=self.parse_release_package
                )
        yield self.build_file_from_response(response, data_type='record_package')

    @handle_error
    def parse_release_package(self, response):
        yield self.build_file_from_response(response, data_type='release_package')
