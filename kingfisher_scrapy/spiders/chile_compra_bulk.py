import json
from datetime import date

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.items import FileError
from kingfisher_scrapy.util import components, date_range_by_month


class ChileCompraBulk(ZipSpider):
    """
    Bulk download documentation
      https://desarrolladores.mercadopublico.cl/OCDS/DescargaMasiva
    Spider arguments
      sample
        Download only data released this month.
    """
    name = 'chile_compra_bulk'
    data_type = 'record_package'

    download_timeout = 99999
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }

    def start_requests(self):
        url = 'https://ocds.blob.core.windows.net/ocds/{0.year:d}{0.month:02d}.zip'

        start = date(2009, 1, 1)
        stop = date.today().replace(day=1)
        if self.sample:
            start = stop
        for d in date_range_by_month(start, stop):
            yield self.build_request(url.format(d), formatter=components(-1))

    def build_file(self, file_name=None, url=None, data=None, data_type=None, encoding='utf-8', post_to_api=True):
        json_data = json.loads(data)
        # some files contain invalid record packages, eg:
        # {
        #   "status": 500,
        #   "detail": "error"
        # }
        if 'status' in json_data and json_data['status'] != 200:
            return FileError({
                'url': url,
                'errors': {'http_code': json_data['status']},
            })
        else:
            return super().build_file(data=data, file_name=file_name, url=url, data_type=data_type, encoding=encoding)
