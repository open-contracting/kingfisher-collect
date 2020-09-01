import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class Kyrgyzstan(LinksSpider):
    """
    Spider arguments
      sample
        Downloads the first release package returned by the main endpoint.
    """
    name = 'kyrgyzstan'
    data_type = 'release_package'
    download_delay = 1
    next_page_formatter = staticmethod(parameters('offset'))

    def start_requests(self):
        url = 'http://ocds.zakupki.gov.kg/api/tendering'
        yield scrapy.Request(url, meta={'file_name': 'offset-0.json'})
