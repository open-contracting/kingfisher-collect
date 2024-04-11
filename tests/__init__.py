import os
from datetime import datetime

from scrapy import Request
from scrapy.http import TextResponse
from scrapy.utils.test import get_crawler

from kingfisher_scrapy.base_spiders import BaseSpider

FILE_LENGTH = 5
FILE_ITEM_LENGTH = FILE_LENGTH + 1


def path(filename):
    return os.path.join('tests', 'fixtures', filename)


def response_fixture(meta=None, url_path='', **kwargs):
    if meta is None:
        meta = {'file_name': 'test'}
    request = Request(f'http://example.com{url_path}', meta=meta)
    kwargs.setdefault('status', 200)
    return TextResponse(request.url, encoding='utf-8', request=request, **kwargs)


def spider_with_crawler(spider_class=BaseSpider, *, settings=None, **kwargs):
    if settings is None:
        settings = {}
    settings.update({'LOG_FORMATTER': 'kingfisher_scrapy.log_formatter.LogFormatter'})
    crawler = get_crawler(spider_class, settings)
    start_time = datetime(2001, 2, 3, 4, 5, 6)
    crawler.stats.set_value('start_time', start_time)
    spider = crawler.spidercls.from_crawler(crawler, name='test', **kwargs)
    return spider
