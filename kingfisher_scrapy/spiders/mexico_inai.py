import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class MexicoINAI(BaseSpider):
    name = 'mexico_inai'

    def start_requests(self):
        yield scrapy.Request(
            url='https://datos.gob.mx/busca/api/3/action/package_search?q=organization:inai&rows=500',
            callback=self.parse_list
        )

    def parse_list(self, response):
        if response.status == 200:
            datas = json.loads(response.body_as_unicode())
            for result in datas['result']['results']:
                for resource in result['resources']:
                    if resource['format'] == 'JSON':
                        yield scrapy.Request(
                            url=resource['url'],
                            meta={
                                'kf_filename': 'redirect-' + hashlib.md5(resource['url'].encode('utf-8')).hexdigest() + '.json',
                                'dont_redirect': True
                            },
                            callback=self.parse_redirect
                        )
        else:
            yield {
                'success': False,
                'file_name': 'list.json',
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }

    def parse_redirect(self, response):
        if response.status == 301:
            url = response.headers['Location'].decode("utf-8").replace("open?", "uc?export=download&")
            yield scrapy.Request(
                url=url,
                meta={'kf_filename': 'data-' + hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'},
                callback=self.parse
            )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }

    def parse(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(
                response,
                response.request.meta['kf_filename'],
                data_type="release_package",
                encoding='utf-8-sig'
            )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
