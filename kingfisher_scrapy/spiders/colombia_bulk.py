import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.util import components, handle_http_error


class ColombiaBulk(CompressedFileSpider):
    """
    Domain
      Colombia Compra Eficiente (CCE)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2005-11'.
        Only supported for 'SECOP1' system.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
        Only supported for 'SECOP1' system.
      system
        Filter by system:

        SECOP1
          Sistema Electrónico para la Contratación Pública (plataforma exclusivamente de publicidad)
        SECOP2
          Sistema Electrónico para la Contratación Pública (todos los procesos de contratación)
        TVEC
          Tienda Virtual del Estado Colombiano (acuerdos marco, agregación de demanda, mínima cuantía)
    Bulk download documentation
      https://www.colombiacompra.gov.co/transparencia/datos-json
    """

    name = 'colombia_bulk'
    date_format = 'year'
    data_type = 'release_in_Release'
    encoding = 'iso-8859-1'
    compressed_file_format = 'json_lines'
    available_systems = {'SECOP1': 'SI', 'SECOP2': 'SECOP2', 'TVEC': 'TVEC'}

    download_timeout = 99999
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }

    @classmethod
    def from_crawler(cls, crawler, system=None, *args, **kwargs):
        spider = super().from_crawler(crawler, system=system, *args, **kwargs)

        if system and spider.system not in spider.available_systems:
            raise SpiderArgumentError(f'spider argument `system`: {spider.system!r} not recognized')

        if spider.from_date and spider.until_date and spider.system != 'SECOP1':
            raise SpiderArgumentError('spider date arguments are only supported for SECOP1 system')

        return spider

    def start_requests(self):
        yield scrapy.Request(
            'https://www.colombiacompra.gov.co/transparencia/datos-json',
            meta={'file_name': 'list.html'},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        urls = response.xpath('//a[@class="enlaces_contenido"]/@href').getall()
        for url in urls:
            if self.system:
                if self.available_systems[self.system] not in url:
                    continue

            if self.from_date and self.until_date:
                if not (self.from_date.year <= int(url[-8:-4]) <= self.until_date.year):
                    continue

            # URL looks like https://apiocds.colombiacompra.gov.co:8443/ArchivosSECOP/Archivos/SI2011.zip
            yield self.build_request(url, formatter=components(-1))
