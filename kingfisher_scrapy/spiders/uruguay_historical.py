from io import BytesIO
from zipfile import ZipFile

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class UruguayHistorical(BaseSpider):
    name = 'uruguay_historical'
    # the files takes too long to be downloaded, so we increase the download timeout
    download_timeout = 1000
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        base_url = 'https://www.gub.uy/agencia-compras-contrataciones-estado/sites/agencia-compras-contrataciones' \
                   '-estado/files/2019-04/OCDS-{}.zip'
        end_year = 2018
        if self.is_sample():
            end_year = 2003
        for year in range(2002, end_year):
            yield scrapy.Request(
                url=base_url.format(year)
            )

    def parse(self, response):
        if response.status == 200:
            zip_files = ZipFile(BytesIO(response.body))
            for finfo in zip_files.infolist():
                data = zip_files.open(finfo.filename).read()
                self.save_response_to_disk(data, finfo.filename, is_response=False)
                yield {
                    'success': True,
                    'file_name': finfo.filename,
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
