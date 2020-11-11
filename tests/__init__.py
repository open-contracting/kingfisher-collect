from datetime import datetime

from scrapy import Request
from scrapy.crawler import Crawler
from scrapy.http import TextResponse

from kingfisher_scrapy.base_spider import BaseSpider


def response_fixture(meta=None, url_path='', **kwargs):
    if meta is None:
        meta = {'file_name': 'test'}
    request = Request(f'http://example.com{url_path}', meta=meta)
    kwargs.setdefault('status', 200)
    return TextResponse(request.url, encoding='utf-8', request=request, **kwargs)


def spider_with_crawler(spider_class=BaseSpider, **kwargs):
    crawler = Crawler(spidercls=spider_class)
    crawler.settings.frozen = False  # otherwise, changes to settings with error
    start_time = datetime(2001, 2, 3, 4, 5, 6)
    crawler.stats.set_value('start_time', start_time)

    spider = crawler.spidercls.from_crawler(crawler, name='test', **kwargs)

    return spider


def spider_with_files_store(files_store, **kwargs):
    spider = spider_with_crawler(**kwargs)
    spider.crawler.settings['FILES_STORE'] = files_store
    spider.crawler.settings['KINGFISHER_API_URI'] = 'http://httpbin.org/anything'
    spider.crawler.settings['KINGFISHER_API_KEY'] = 'xxx'

    return spider
