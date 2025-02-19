import logging
import re
from datetime import datetime

import pytest
from scrapy.crawler import Crawler, CrawlerRunner
from scrapy.http import Response
from scrapy.utils.project import get_project_settings

from kingfisher_scrapy.exceptions import MissingEnvVarError

# See scrapy.cmdline.execute
settings = get_project_settings()
runner = CrawlerRunner(settings)


# See scrapy.commands.list
@pytest.mark.parametrize('spider_name', runner.spider_loader.list())
def test_start_requests_http_error(spider_name, caplog):
    caplog.set_level(logging.ERROR)

    # See scrapy.crawler.CrawlerRunner._create_crawler
    spidercls = runner.spider_loader.load(spider_name)
    crawler = Crawler(spidercls, runner.settings)
    crawler._apply_settings()  # noqa: SLF001
    start_time = datetime(2001, 2, 3, 4, 5, 6)
    crawler.stats.set_value('start_time', start_time)

    try:
        # See scrapy.crawler.Crawler._create_spider
        spider = crawler.spidercls.from_crawler(crawler)

        for request in spider.start_requests():
            # See scrapy.core.scraper.Scraper.call_spider
            callback = request.callback or spider.parse

            response = Response('http://example.com', status=555, request=request)
            # If `max_attempts` is set, the spider handles (and retries) error responses.
            if hasattr(spider, 'max_attempts'):
                response.request.meta['retries'] = spider.max_attempts
                response.headers['Retry-After'] = 1
            items = list(callback(response))

            assert len(items) == 0
            for record in caplog.records:
                assert re.search(
                    r"^status=555 message='[^']*' request=<(GET|POST) \S+> file_name=\S+$",
                    record.message,
                )
    except MissingEnvVarError as e:
        pytest.skip(f'{spidercls.name}: {e}')


@pytest.mark.parametrize('spider_name', runner.spider_loader.list())
def test_start_urls_start_requests(spider_name):
    spidercls = runner.spider_loader.load(spider_name)

    assert 'start_urls' not in spidercls.__dict__ or 'start_requests' not in spidercls.__dict__
