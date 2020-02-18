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
            datas = json.loads(response.body_as_unicode())
            if self.sample:
                datas = [datas[0]]
            for data in datas:
                yield scrapy.Request(
                    url=data['URIContract'],
                    meta={'kf_filename': 'id%s.json' % data['ocid']},
                    callback=self.parse_record_package
                )
        else:
            yield {
                'success': False,
                'file_name': 'list.json',
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }

    def parse_record_package(self, response):
        if response.status == 200:
            json_data = json.loads(response.body_as_unicode())
            if 'packages' in json_data:
                for url in json_data['packages']:
                    yield scrapy.Request(
                        url=url,
                        meta={'kf_filename': 'packages-%s.json' % hashlib.md5(url.encode('utf-8')).hexdigest()},
                        callback=self.parse_release_package
                    )
            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type="record_package")
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }

    def parse_release_package(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type="release_package")
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
