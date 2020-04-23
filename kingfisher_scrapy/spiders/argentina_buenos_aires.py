import hashlib
import json
from io import BytesIO
from zipfile import ZipFile

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class ArgentinaBuenosAires(BaseSpider):
    name = 'argentina_buenos_aires'
    start_urls = ['https://data.buenosaires.gob.ar/api/3/action/package_show?id=buenos-aires-compras']
    # the data list service takes too long to be downloaded, so we increase the download timeout
    download_timeout = 1000

    def start_requests(self):
        yield scrapy.Request(
            url='https://data.buenosaires.gob.ar/api/3/action/package_show?id=buenos-aires-compras',
            callback=self.parse_list
        )

    @staticmethod
    def parse_list(response):
        if response.status == 200:
            data = json.loads(response.text)
            for resource in data['result']['resources']:
                if resource['format'].upper() == 'JSON':
                    yield scrapy.Request(
                        url=resource['url']
                    )
        else:
            yield {
                'success': False,
                'file_name': 'list.json',
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }

    def parse(self, response):
        yield from self.parse_zipfile(response, 'release', file_format='release_package')
