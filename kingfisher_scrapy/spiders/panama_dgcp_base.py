import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class PanamaDGCPBase(LinksSpider):
    # BaseSpider
    root_path = 'package'

    # LinksSpider
    formatter = staticmethod(parameters('page'))
    next_pointer = '/next'

    # Local
    base_url = 'https://ocds.panamacompraencifras.gob.pa/'

    # url_path must be provided by subclasses.

    def start_requests(self):
        yield scrapy.Request(f'{self.base_url}{self.url_path}?page=1', meta={'file_name': 'page-1.json'})
