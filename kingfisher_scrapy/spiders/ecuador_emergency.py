import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class EcuadorEmergency(SimpleSpider):
    """
    Bulk download documentation
      https://portal.compraspublicas.gob.ec/sercop/data-estandar-ocds/
    """
    name = 'ecuador_emergency'
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://datosabiertos.compraspublicas.gob.ec/OCDS/'
        yield scrapy.Request(url, meta={'file_name': 'list.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        html_urls = response.xpath('//a/@href').getall()
        for html_url in html_urls:
            yield self.build_request(response.request.url + html_url, formatter=components(-1))
