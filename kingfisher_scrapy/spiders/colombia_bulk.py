import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class ColombiaBulk(CompressedFileSpider):
    """
    Domain
      Colombia Compra Eficiente (CCE)
    Bulk download documentation
      https://www.colombiacompra.gov.co/transparencia/datos-json
    """

    name = 'colombia_bulk'
    data_type = 'release'
    encoding = 'iso-8859-1'
    compressed_file_format = 'json_lines'
    root_path = 'Release'

    download_timeout = 99999
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }

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
            # URL looks like https://apiocds.colombiacompra.gov.co:8443/ArchivosSECOP/Archivos/SI2011.zip
            yield self.build_request(url, formatter=components(-1))
