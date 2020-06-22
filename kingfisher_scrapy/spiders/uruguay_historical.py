from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.util import components, date_range_by_year


class UruguayHistorical(ZipSpider):
    """
    Bulk download documentation
      https://www.gub.uy/agencia-compras-contrataciones-estado/datos-y-estadisticas/datos/open-contracting
    Spider arguments
      sample
        Download only data released on 2002.
    """
    name = 'uruguay_historical'
    data_type = 'release_package'

    # the files takes too long to be downloaded, so we increase the download timeout
    download_timeout = 1000
    custom_settings = {
        # It seems some websites don't like it and block when your user agent is not a browser.
        # see https://github.com/scrapy/scrapy/issues/3103
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/37.0.2049.0 Safari/537.36',
    }

    def start_requests(self):
        start = 2002
        stop = 2017
        if self.sample:
            start = stop

        pattern = 'https://www.gub.uy/agencia-compras-contrataciones-estado/sites' \
                  '/agencia-compras-contrataciones-estado/files/2019-04/OCDS-{}.zip'
        for year in date_range_by_year(start, stop):
            yield self.build_request(pattern.format(year), formatter=components(-1))
