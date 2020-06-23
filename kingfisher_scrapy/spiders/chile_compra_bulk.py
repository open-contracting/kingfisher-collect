from datetime import date

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.util import components, date_range_by_month


class ChileCompraBulk(ZipSpider):
    """
    Bulk download documentation
      https://desarrolladores.mercadopublico.cl/OCDS/DescargaMasiva
    Spider arguments
      sample
        Download only data released on February 2017.
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
