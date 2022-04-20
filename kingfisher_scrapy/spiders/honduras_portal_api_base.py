import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError


class HondurasPortalAPIBase(IndexSpider):
    download_delay = 0.9

    # IndexSpider
    total_pages_pointer = '/pages'

    # Local
    available_publishers = ['oncae', 'sefin']
    # start_url must be provided by subclasses.

    @classmethod
    def from_crawler(cls, crawler, publisher=None, *args, **kwargs):
        spider = super().from_crawler(crawler, publisher=publisher, *args, **kwargs)
        if publisher and spider.publisher not in spider.available_publishers:
            raise SpiderArgumentError(f'spider argument `publisher`: {spider.publisher!r} not recognized')

        return spider

    def start_requests(self):
        url = self.start_url
        if self.publisher:
            url = f'{url}&publisher={self.publisher}'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)
