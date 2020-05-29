import warnings

import pytest
import scrapy
from scrapy.crawler import Crawler, CrawlerRunner
from scrapy.exceptions import CloseSpider
from scrapy.http import Response
from scrapy.utils.deprecate import method_is_overridden
from scrapy.utils.project import get_project_settings

from kingfisher_scrapy.items import FileError

# See scrapy.cmdline.execute
settings = get_project_settings()
runner = CrawlerRunner(settings)


# See scrapy.commands.list
@pytest.mark.parametrize('spider_name', runner.spider_loader.list())
def test_start_requests_http_error(spider_name):
    # See scrapy.crawler.CrawlerRunner._create_crawler
    spidercls = runner.spider_loader.load(spider_name)
    crawler = Crawler(spidercls, runner.settings)

    try:
        # See scrapy.crawler.Crawler._create_spider
        spider = crawler.spidercls.from_crawler(crawler)
        for request in spider.start_requests():
            # See scrapy.core.scraper.Scraper.call_spider
            callback = request.callback or spider.parse

            response = Response('http://example.com', status=555, request=request)
            items = list(callback(response))

            assert len(items) == 1
            for item in items:
                assert isinstance(item, FileError)
                assert len(item) == 3
                assert item['errors'] == {'http_code': 555}
                assert item['file_name']
                assert item['url']
    except CloseSpider as e:
        warnings.warn('{}: {}'.format(spidercls.name, e.reason))


@pytest.mark.parametrize('spider_name', runner.spider_loader.list())
def test_start_urls_start_requests(spider_name):
    spidercls = runner.spider_loader.load(spider_name)

    assert 'start_urls' not in spidercls.__dict__ or 'start_requests' not in spidercls.__dict__
