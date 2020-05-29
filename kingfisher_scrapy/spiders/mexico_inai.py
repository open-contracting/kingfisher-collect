import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class MexicoINAI(BaseSpider):
    name = 'mexico_inai'

    def start_requests(self):
        yield scrapy.Request(
            url='https://datos.gob.mx/busca/api/3/action/package_search?q=organization:inai&rows=500',
            meta={'kf_filename': 'list.json'},
            callback=self.parse_list
        )

    @handle_error
    def parse_list(self, response):
        datas = json.loads(response.text)
        for result in datas['result']['results']:
            for resource in result['resources']:
                if resource['format'] == 'JSON':
                    kf_filename = 'redirect-' + hashlib.md5(resource['url'].encode('utf-8')).hexdigest() + '.json'
                    yield scrapy.Request(
                        url=resource['url'],
                        meta={
                            'kf_filename': kf_filename,
                            'dont_redirect': True
                        },
                        callback=self.parse_redirect
                    )

    def parse_redirect(self, response):
        if response.status == 301:
            url = response.headers['Location'].decode("utf-8").replace("open?", "uc?export=download&")
            yield scrapy.Request(
                url=url,
                meta={'kf_filename': 'data-' + hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'},
                callback=self.parse
            )
        else:
            yield self.build_file_error_from_response(response)

    @handle_error
    def parse(self, response):
        yield self.build_file_from_response(response, data_type='release_package', encoding='utf-8-sig')
