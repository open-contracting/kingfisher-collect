from zipfile import ZipFile

import scrapy
from io import BytesIO

from kingfisher_scrapy.base_spider import BaseSpider


class Uruguay(BaseSpider):
    name = 'uruguay_historical'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        base_url = 'https://www.gub.uy/agencia-compras-contrataciones-estado/sites/agencia-compras-contrataciones' \
                   '-estado/files/2019-04/OCDS-{}.zip '
        for year in range(2002, 2018):
            yield scrapy.Request(
                url=base_url.format(year)
            )

    def parse(self, response):
        if response.status == 200:
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
