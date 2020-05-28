import scrapy

from kingfisher_scrapy.base_spider import ZipSpider


class UruguayHistorical(ZipSpider):
    """
    API documentation
      https://www.gub.uy/agencia-compras-contrataciones-estado/datos-y-estadisticas/datos/open-contracting
    Spider arguments
      sample
        Download only data released on 2002.
    """
    name = 'uruguay_historical'
    # the files takes too long to be downloaded, so we increase the download timeout
    download_timeout = 1000
    custom_settings = {
        # It seems some websites don't like it and block when your user agent is not a browser.
        # see https://github.com/scrapy/scrapy/issues/3103
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/37.0.2049.0 Safari/537.36',
    }

    parse_zipfile_kwargs = {'data_type': 'release_package'}

    def start_requests(self):
        base_url = 'https://www.gub.uy/agencia-compras-contrataciones-estado/sites/agencia-compras-contrataciones' \
                   '-estado/files/2019-04/OCDS-{}.zip'
        end_year = 2018
        if self.sample:
            end_year = 2003
        for year in range(2002, end_year):
            yield scrapy.Request(
                url=base_url.format(year)
            )
