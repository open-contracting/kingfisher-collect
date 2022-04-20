import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class NigeriaEkitiState(SimpleSpider):
    """
    Domain
      Nigeria Ekiti State Open Contracting Portal
    """
    name = 'nigeria_ekiti_state'

    # SimpleSpider
    data_type = 'release_package'

    # Local
    url_prefix = 'https://ocds.bpp.ekitistate.gov.ng/'

    def start_requests(self):
        url = f'{self.url_prefix}Home/Procurements/'
        yield scrapy.Request(url, meta={'file_name': 'all.html'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        pattern = '//table[@id="datable_3"]/tbody/tr/td[2]/span/a/@href'
        for item in response.xpath(pattern).re("[0-9]+"):
            yield self.build_request(f'{self.url_prefix}openapi/packagesapi/{item}', formatter=components(-1))
