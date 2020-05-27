import hashlib

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.util import handle_error


class ChileCompraBulk(ZipSpider):
    name = 'chile_compra_bulk'
    download_warnsize = 0
    download_timeout = 99999
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }

    def start_requests(self):
        url = 'https://ocds.blob.core.windows.net/ocds/{}{}.zip'
        if self.sample:
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

    @handle_error
    def parse(self, response):
        yield from self.parse_zipfile(response, data_type='record_package')
