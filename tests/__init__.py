from datetime import datetime

from scrapy import Request
from scrapy.crawler import Crawler
from scrapy.http import TextResponse

from kingfisher_scrapy.base_spider import BaseSpider


def response_fixture(**kwargs):
    request = Request('http://example.com', meta={'file_name': 'test'})
    if 'status' not in kwargs:
        kwargs['status'] = 200
    if 'body' not in kwargs:
        kwargs['body'] = b'{"links": {"next": "http://example.com/next"}}'
    return TextResponse(request.url, encoding='utf-8', request=request, **kwargs)


def spider_with_crawler(spider_class=BaseSpider, **kwargs):
    crawler = Crawler(spidercls=spider_class)
    crawler.settings.frozen = False  # otherwise, changes to settings with error
    start_time = datetime(2001, 2, 3, 4, 5, 6)
    crawler.stats.set_value('start_time', start_time)

    spider = crawler.spidercls.from_crawler(crawler, name='test', **kwargs)

    return spider
