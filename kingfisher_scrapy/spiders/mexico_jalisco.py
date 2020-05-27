import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class MexicoJalisco(BaseSpider):
    name = 'mexico_jalisco'

    def start_requests(self):
        yield scrapy.Request(
            url='https://contratacionesabiertas.jalisco.gob.mx/OCApi/2017/contracts',
            meta={'kf_filename': 'list.json'},
            callback=self.parse_list
        )

    def parse_list(self, response):
        if response.status == 200:
            datas = json.loads(response.text)
            if self.sample:
                datas = [datas[0]]
            for data in datas:
                yield scrapy.Request(
                    url=data['URIContract'],
                    meta={'kf_filename': 'id%s.json' % data['ocid']},
                    callback=self.parse_record_package
                )
        else:
            yield self.build_file_error_from_response(response, filename='list.json')

    def parse_record_package(self, response):
        if response.status == 200:
            json_data = json.loads(response.text)
            if 'packages' in json_data:
                for url in json_data['packages']:
                    yield scrapy.Request(
                        url=url,
                        meta={'kf_filename': 'packages-%s.json' % hashlib.md5(url.encode('utf-8')).hexdigest()},
                        callback=self.parse_release_package
                    )
            yield self.build_file_from_response(response, response.request.meta['kf_filename'],
                                                data_type='record_package')
        else:
            yield self.build_file_error_from_response(response)

    def parse_release_package(self, response):
        if response.status == 200:
            yield self.build_file_from_response(response, response.request.meta['kf_filename'],
                                                data_type='release_package')
        else:
            yield self.build_file_error_from_response(response)
