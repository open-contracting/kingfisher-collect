import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class MexicoQuienEsQuienBase(IndexSpider):
    download_delay = 0.9

    # BaseSpider
    root_path = 'data.item'

    # IndexSpider
    count_pointer = '/data/index/contracts/count'
    limit = 1000  # >= 10000 causes "Search size is bigger than 10000. Elasticsearch does not allow it."

    def start_requests(self):
        url = 'https://api.quienesquien.wiki/v3/sources'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)
