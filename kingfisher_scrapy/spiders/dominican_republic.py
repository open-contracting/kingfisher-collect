import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class DominicanRepublic(CompressedFileSpider):
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
    name = 'dominican_republic'
    date_format = 'year'
    data_type = 'release_package'
    default_from_date = '2018'
    compressed_file_format = 'release_package'

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
            if '/JSON_DGCP_' in url:
                if self.from_date and self.until_date:
                    date = int(url[-8:-4])
                    if not (self.from_date.year <= date <= self.until_date.year):
                        continue
                yield self.build_request(url, formatter=components(-1))
