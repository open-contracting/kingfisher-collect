import hashlib
from io import BytesIO
from zipfile import ZipFile

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class ChileCompraBulk(BaseSpider):
    name = 'chile_compra_bulk'
    download_warnsize = 0
    download_timeout = 99999
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }

    def start_requests(self):
        url = 'https://ocds.blob.core.windows.net/ocds/{}{}.zip'
        if self.is_sample():
            years = ['2017']
            months = ['02']
        else:
            years = range(2017, 2020)
            months = ['0{}'.format(m) if m < 10 else str(m) for m in range(1, 13)]

        for year in years:
            for month in months:
                yield scrapy.Request(
                    url.format(year, month),
                    meta={'kf_filename': hashlib.md5((url).encode('utf-8')).hexdigest()}
                )

    def parse(self, response):
        if response.status == 200:
            zip_file = ZipFile(BytesIO(response.body))
            for finfo in zip_file.infolist():
                data = zip_file.open(finfo.filename).read()
                yield self.save_data_to_disk(
                    data,
                    response.request.meta['kf_filename'] + finfo.filename,
                    data_type='record_package',
                    url=response.request.url
                )
        else:
            yield {
                'success': False,
                'kf_filename': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
