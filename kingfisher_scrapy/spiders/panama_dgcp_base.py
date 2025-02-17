import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider


class PanamaDGCPBase(IndexSpider):
    # IndexSpider
    page_count_pointer = '/pages'

    # url_path must be provided by subclasses.

    def start_requests(self):
        yield scrapy.Request(
            f'https://ocds.panamacompraencifras.gob.pa/{self.url_path}?page=1&DescendingOrder=true',
            meta={'file_name': 'page-1.json'},
            callback=self.parse_list,
        )
