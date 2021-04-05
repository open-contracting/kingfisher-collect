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
    download_timeout = 99999
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }

    # BaseSpider
    line_delimited = True
    root_path = 'Release'
    root_path_max_length = 1
    skip_pluck = 'Already covered (see code for details)'  # colombia

    # SimpleSpider
    data_type = 'release'
    encoding = 'iso-8859-1'

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
