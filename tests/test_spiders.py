import warnings
from datetime import datetime

import pytest
from scrapy.crawler import Crawler, CrawlerRunner
from scrapy.http import Response
from scrapy.utils.project import get_project_settings

from kingfisher_scrapy.exceptions import MissingEnvVarError
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
    start_time = datetime(2001, 2, 3, 4, 5, 6)
    crawler.stats.set_value('start_time', start_time)

    try:
        # See scrapy.crawler.Crawler._create_spider
        spider = crawler.spidercls.from_crawler(crawler)
        for request in spider.start_requests():
            # See scrapy.core.scraper.Scraper.call_spider
            callback = request.callback or spider.parse

            response = Response('http://example.com', status=555, request=request)
            items = list(callback(response))

            # if number_of_retries is set the spider is handling its own errors and could retry after an error
            if not hasattr(spider, 'number_of_retries'):

                assert len(items) == 1
                for item in items:
                    assert type(item) is FileError
                    assert len(item) == 3
                    assert item['errors'] == {'http_code': 555}
                    assert item['file_name']
                    assert item['url']
    except MissingEnvVarError as e:
        warnings.warn(f'{spidercls.name}: {e}')


@pytest.mark.parametrize('spider_name', runner.spider_loader.list())
def test_start_urls_start_requests(spider_name):
    spidercls = runner.spider_loader.load(spider_name)

    assert 'start_urls' not in spidercls.__dict__ or 'start_requests' not in spidercls.__dict__
