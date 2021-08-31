import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class MexicoQuienEsQuienBase(IndexSpider):
    download_delay = 0.9

    # BaseSpider
    root_path = 'data.item'

    # IndexSpider
    count_pointer = '/data/index/contracts/count'
    limit = 1000
    yield_list_results = False

    def start_requests(self):
        yield scrapy.Request(
            'https://api.quienesquien.wiki/v3/sources',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )
