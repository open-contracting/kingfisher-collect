import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class EcuadorEmergency(SimpleSpider):
    """
    Domain
      Servicio Nacional de Contratación Pública
    Bulk download documentation
      https://portal.compraspublicas.gob.ec/sercop/data-estandar-ocds/
    """
    name = 'ecuador_emergency'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://datosabiertos.compraspublicas.gob.ec/OCDS/'
        yield scrapy.Request(url, meta={'file_name': 'list.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        html_urls = response.xpath('//a/@href').getall()
        if html_urls:
            # Each link contains different versions of SERCOP's emergency dataset, only the newest should be downloaded
            # URL format: ./archivos/ocds-YYYY-MM-DD.json
            html_urls.sort(reverse=True)
            yield self.build_request(f'{response.request.url}{html_urls[0]}', formatter=components(-1))
