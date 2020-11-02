import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.util import parameters


class HondurasPortalBase(IndexSpider):
    next_pointer = '/next'
    formatter = staticmethod(parameters('page'))
    total_pages_pointer = '/pages'
    publishers = ['oncae', 'sefin']

    download_delay = 0.9

    @classmethod
    def from_crawler(cls, crawler, publisher=None, *args, **kwargs):
        spider = super().from_crawler(crawler, publisher=publisher, *args, **kwargs)
        if publisher and spider.publisher not in spider.publishers:
            raise SpiderArgumentError(f'spider argument `publisher`: {spider.publisher!r} not recognized')

        return spider

    def start_requests(self):
        url = self.url
        if self.publisher:
            url = f'{url}&publisher={self.publisher}'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)
