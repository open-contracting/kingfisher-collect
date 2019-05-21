import json
from io import BytesIO
from zipfile import ZipFile

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class BuenosAires(BaseSpider):
    name = 'buenos_aires'
    start_urls = ['https://data.buenosaires.gob.ar/api/3/action/package_show?id=buenos-aires-compras']
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }
    # the data list service takes too long to be downloaded, so we increase the download timeout
    download_timeout = 1000

    def start_requests(self):
        yield scrapy.Request(
            url='https://data.buenosaires.gob.ar/api/3/action/package_show?id=buenos-aires-compras',
            meta={'type': 'meta'}
        )

    def parse(self, response):
        if response.status == 200:
            print(response.request.meta)
            if response.request.meta['type'] == 'meta':
                data = json.loads(response.body_as_unicode())
                for resource in data['result']['resources']:
                    if resource['format'].upper() == 'JSON':
                        yield scrapy.Request(
                            url=resource['url'],
                            meta={'kf_filename': 'bsas_release.json', 'type': 'data'}
                        )
            else:
                zip_file = ZipFile(BytesIO(response.body))
                data = zip_file.open('bsas_release.json').read()
                self.save_response_to_disk(data, response.request.meta['kf_filename'], is_response=False)
                yield {
                    'success': True,
                    'file_name': response.request.meta['kf_filename'],
                    'data_type': 'release_package',
                    'url': response.request.url,
                }
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
