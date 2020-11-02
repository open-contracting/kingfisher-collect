import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class Kyrgyzstan(LinksSpider):
    """
    Domain
      Ministry of Finance
    """
    name = 'kyrgyzstan'
    data_type = 'release_package'
    next_page_formatter = staticmethod(parameters('offset'))

    def start_requests(self):
        yield scrapy.Request('http://ocds.zakupki.gov.kg/api/tendering', meta={'file_name': 'offset-0.json'})
