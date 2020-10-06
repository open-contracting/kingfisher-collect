from kingfisher_scrapy.base_spider import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.util import components


class UruguayHistorical(CompressedFileSpider, PeriodicSpider):
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
    default_from_date = '2002'
    default_until_date = '2017'
    date_format = 'year'
    custom_settings = {
        # It seems some websites don't like it and block when your user agent is not a browser.
        # see https://github.com/scrapy/scrapy/issues/3103
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/37.0.2049.0 Safari/537.36',
    }
    pattern = 'https://www.gub.uy/agencia-compras-contrataciones-estado/sites' \
              '/agencia-compras-contrataciones-estado/files/2019-04/OCDS-{}.zip'

    def get_formatter(self):
        return components(-1)
