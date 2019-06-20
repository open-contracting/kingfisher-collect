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
        # It seems some websites don't like it and block when your user agent is not a browser.
        # see https://github.com/scrapy/scrapy/issues/3103
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/37.0.2049.0 Safari/537.36',
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
                yield self.save_response_to_disk(data, finfo.filename, is_response=False, data_type='release_package')

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
