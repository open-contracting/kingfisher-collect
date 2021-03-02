import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components


class MexicoPlataformaDigitalNacional(CompressedFileSpider):

    """
    Domain
      Plataforma Digital Nacional
    Bulk download documentation
      https://plataformadigitalnacional.org/contrataciones
    """
    name = 'mexico_plataforma_digital_nacional'
    data_type = 'release'
    root_path = 'item'

    def start_requests(self):
        yield scrapy.Request(
            'https://drive.google.com/uc?id=1XOYDLVv-RqcMs8_hzkZ0fjC9FYh2psFw',
            meta={'file_name': 'list.html'},
            callback=self.parse_list,
        )

    def parse_list(self, response):
        url = response.xpath('//a[@id="uc-download-link"]/@href').get()
        yield self.build_request(url=f'https://drive.google.com{url}',
                                 formatter=components(-1),
                                 meta={'file_name': 'contrataciones.zip'})
