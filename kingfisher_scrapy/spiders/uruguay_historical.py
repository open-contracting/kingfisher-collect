import datetime

import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class UruguayHistorical(CompressedFileSpider):
    """
    Domain
      Agencia Reguladora de Compras Estatales (ARCE)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2002'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    Bulk download documentation
      https://www.gub.uy/agencia-compras-contrataciones-estado/datos-y-estadisticas/datos/open-contracting
    """
    name = 'uruguay_historical'
    download_timeout = 1000

    # BaseSpider
    date_format = 'year'
    default_from_date = '2002'
    skip_pluck = 'Already covered (see code for details)'  # uruguay_releases

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        # A CKAN API JSON response.
        url = 'https://catalogodatos.gub.uy/api/3/action/package_show?id=arce-datos-historicos-de-compras'
        yield scrapy.Request(url, meta={'file_name': 'package_show.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for resource in response.json()['result']['resources']:
            if resource['format'].upper() == 'JSON':
                url = resource['url']
                if self.from_date and self.until_date:
                    # URL looks like
                    # https://catalogodatos.gub.uy/dataset/44d3-b09c/resource/1e39-453d/download/ocds-2002.zip
                    url_year = int(url.split('-')[-1].split('.')[0])
                    url_date = datetime.datetime(url_year, 1, 1)
                    if not (self.from_date <= url_date <= self.until_date):
                        continue
                yield self.build_request(url, formatter=components(-1))  # filename containing year
