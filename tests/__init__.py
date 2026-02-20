import datetime
import os

from scrapy import Request
from scrapy.crawler import CrawlerRunner
from scrapy.http import TextResponse
from scrapy.statscollectors import MemoryStatsCollector
from scrapy.utils.test import get_reactor_settings

from kingfisher_scrapy.base_spiders import BaseSpider
from kingfisher_scrapy.log_formatter import LogFormatter

FILE_LENGTH = 5
FILE_ITEM_LENGTH = FILE_LENGTH + 1


def path(filename):
    return os.path.join("tests", "fixtures", filename)


def response_fixture(meta=None, url_path="", **kwargs):
    if meta is None:
        meta = {"file_name": "test"}
    request = Request(f"http://example.com{url_path}", meta=meta)
    kwargs.setdefault("status", 200)
    return TextResponse(request.url, encoding="utf-8", request=request, **kwargs)


def spider_with_crawler(spider_class=BaseSpider, *, settings=None, **kwargs):
    if settings is None:
        settings = {}
    if not hasattr(spider_class, "name"):
        spider_class = type("TestSpider", (spider_class,), {"name": "test"})
    settings.update({"LOG_FORMATTER": "kingfisher_scrapy.log_formatter.LogFormatter"})

    # scrapy.utils.test.get_crawler() freezes the settings too early with crawler._apply_settings().
    runner = CrawlerRunner({**get_reactor_settings(), **settings})
    crawler = runner.create_crawler(spider_class)
    # Before calling `self._apply_settings()`, Crawler.crawl sets `self.spider = self._create_spider(*args, **kwargs)`,
    # which returns `self.spidercls.from_crawler(self, *args, **kwargs)`. Add a subset of `self._apply_settings()`.
    crawler.spider = crawler.spidercls.from_crawler(crawler, **kwargs)
    crawler.stats = MemoryStatsCollector(crawler)
    crawler.logformatter = LogFormatter.from_crawler(crawler)

    # CoreStats.spider_opened
    start_time = datetime.datetime(2001, 2, 3, 4, 5, 6)
    crawler.stats.set_value("start_time", start_time)

    return crawler.spider
