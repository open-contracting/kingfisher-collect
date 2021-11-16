import re

import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class DominicanRepublicBulk(CompressedFileSpider):
    """
    Domain
      Dirección General de Contrataciones Públicas (DGCP)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2018'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    Bulk download documentation
      https://www.dgcp.gob.do/estandar-mundial-ocds/
    """
    name = 'dominican_republic_bulk'
    date_format = 'year'
    default_from_date = '2018'

    # BaseSpider
    skip_pluck = 'Already covered (see code for details)'  # dominican_republic_api

    # SimpleSpider
    data_type = 'release_package'

    # CompressedFileSpider
    resize_package = True

    def start_requests(self):
        yield scrapy.Request(
            'https://www.dgcp.gob.do/estandar-mundial-ocds/',
            meta={'file_name': 'list.html'},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        urls = response.css('.download::attr(href)').getall()
        for url in urls:
            if 'JSON' in url:
                if self.from_date and self.until_date:
                    # URL looks like https://www.dgcp.gob.do/new_dgcp/documentos/andres/JSON_DGCP_2019.rar
                    # but also https://www.dgcp.gob.do/new_dgcp/documentos/andres/JSON-20200713T141805Z-001.zip
                    # so we look for the first 4 digits in the URL
                    year = int(re.search(r'\d{4}', url).group(0))
                    if not (self.from_date.year <= year <= self.until_date.year):
                        continue
                yield self.build_request(url, formatter=components(-1))
