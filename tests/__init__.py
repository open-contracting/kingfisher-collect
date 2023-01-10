from datetime import datetime

from scrapy import Request
from scrapy.http import TextResponse
from scrapy.utils.test import get_crawler

from kingfisher_scrapy.base_spiders import BaseSpider


class ExpectedError(Exception):
    pass


def response_fixture(meta=None, url_path='', **kwargs):
    if meta is None:
        meta = {'file_name': 'test'}
    request = Request(f'http://example.com{url_path}', meta=meta)
    kwargs.setdefault('status', 200)
    return TextResponse(request.url, encoding='utf-8', request=request, **kwargs)


def spider_with_crawler(spider_class=BaseSpider, *, settings=None, **kwargs):
    crawler = get_crawler(spider_class, settings)
    start_time = datetime(2001, 2, 3, 4, 5, 6)
    crawler.stats.set_value('start_time', start_time)

    spider = crawler.spidercls.from_crawler(crawler, name='test', **kwargs)

    return spider


def spider_with_files_store(files_store, settings=None, **kwargs):
    crawler_settings = {
        'FILES_STORE': files_store,
        'KINGFISHER_API_URI': 'http://httpbin.org/anything',
        'KINGFISHER_API_KEY': 'xxx',
        'KINGFISHER_API2_URL': 'http://httpbin.org/anything',
    }
    if settings:
        crawler_settings.update(settings)

    spider = spider_with_crawler(settings=crawler_settings, **kwargs)

    return spider
