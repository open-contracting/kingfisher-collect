from datetime import datetime

from scrapy.crawler import Crawler

from kingfisher_scrapy.base_spider import BaseSpider


def spider_with_crawler(sample=False):
    crawler = Crawler(spidercls=BaseSpider)
    crawler.settings.frozen = False  # otherwise, changes to settings with error
    start_time = datetime(2001, 2, 3, 4, 5, 6)
    crawler.stats.set_value('start_time', start_time)

    spider = crawler.spidercls.from_crawler(crawler, 'test')
    spider.sample = sample

    return spider
