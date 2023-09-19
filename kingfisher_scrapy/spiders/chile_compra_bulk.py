import json

from kingfisher_scrapy.base_spiders import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.items import FileError
from kingfisher_scrapy.util import components


class ChileCompraBulk(CompressedFileSpider, PeriodicSpider):
    """
    Domain
      ChileCompra
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2009-01'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
    Bulk download documentation
      https://desarrolladores.mercadopublico.cl/OCDS/DescargaMasiva
    """
    name = 'chile_compra_bulk'
    download_timeout = 99999
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }

    # BaseSpider
    skip_pluck = 'Already covered (see code for details)'  # chile_compra_records

    # SimpleSpider
    data_type = 'record_package'

    # BaseSpider
    date_format = 'year-month'
    default_from_date = '2009-01'

    # PeriodicSpider
    pattern = 'https://ocds.blob.core.windows.net/ocds/{0.year:d}{0.month:02d}.zip'
    formatter = staticmethod(components(-1))  # filename containing year-month

    def build_file(self, file_name=None, url=None, data=None, **kwargs):
        json_data = json.loads(data)
        # Some files contain invalid record packages, e.g.:
        # {
        #   "status": 500,
        #   "detail": "error"
        # }
        if 'status' in json_data and json_data['status'] != 200:
            json_data['http_code'] = json_data['status']
            return FileError({
                'file_name': file_name,
                'url': url,
                'errors': json_data,
            })
        else:
            return super().build_file(file_name=file_name, url=url, data=data, **kwargs)
