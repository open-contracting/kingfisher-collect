import json
from io import BytesIO
from zipfile import ZipFile
import hashlib

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class BuenosAires(BaseSpider):
    name = 'buenos_aires'
    start_urls = ['https://data.buenosaires.gob.ar/api/3/action/package_show?id=buenos-aires-compras']
    # the data list service takes too long to be downloaded, so we increase the download timeout
    download_timeout = 1000

    def start_requests(self):
        yield scrapy.Request(
            url='https://data.buenosaires.gob.ar/api/3/action/package_show?id=buenos-aires-compras',
            meta={'type': 'meta'}
        )

    def parse(self, response):
        if response.status == 200:
            if response.request.meta['type'] == 'meta':
                data = json.loads(response.body_as_unicode())
                for resource in data['result']['resources']:
                    if resource['format'].upper() == 'JSON':
                        yield scrapy.Request(
                            url=resource['url'],
                            meta={'type': 'data'}
                        )
            else:
                zip_file = ZipFile(BytesIO(response.body))
                for finfo in zip_file.infolist():
                    data = zip_file.open(finfo.filename).read()
                    yield self.save_data_to_disk(data, finfo.filename, data_type='release_package', url=response.request.url)
        else:
            yield {
                'success': False,
                'file_name': hashlib.md5(response.request.url.encode('utf-8')).hexdigest() + '.json',
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
