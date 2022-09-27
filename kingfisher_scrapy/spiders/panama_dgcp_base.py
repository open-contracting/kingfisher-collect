import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider


class PanamaDGCPBase(IndexSpider):
    # BaseSpider
    root_path = 'package'

    # IndexSpider
    page_count_pointer = '/pages'

    # url_path must be provided by subclasses.

    def start_requests(self):
        url = 'https://ocds.panamacompraencifras.gob.pa/'
        yield scrapy.Request(f'{url}{self.url_path}?page=1&DescendingOrder=true',
                             meta={'file_name': 'page-1.json'}, callback=self.parse_list)
