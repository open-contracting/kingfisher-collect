import logging
import re
from datetime import datetime, timedelta, timezone

import pytest
from scrapy.crawler import Crawler, CrawlerRunner
from scrapy.http import Response
from scrapy.utils.project import get_project_settings

from kingfisher_scrapy.exceptions import MissingEnvVarError

# See scrapy.cmdline.execute
settings = get_project_settings()
runner = CrawlerRunner(settings)


# See scrapy.commands.list
@pytest.mark.parametrize("spider_name", runner.spider_loader.list())
async def test_start_http_error(spider_name, caplog):
    caplog.set_level(logging.ERROR)

    # See scrapy.crawler.CrawlerRunner._create_crawler
    spidercls = runner.spider_loader.load(spider_name)
    crawler = Crawler(spidercls, runner.settings)
    crawler._apply_settings()  # noqa: SLF001
    start_time = datetime(2001, 2, 3, 4, 5, 6)
    crawler.stats.set_value("start_time", start_time)

    try:
        kwargs = {}
        # colombia_bulk errors if until_date is set but system is not 'SECOP1'.
        if (default_from_date := getattr(spidercls, "default_from_date", None)) and spider_name != "colombia_bulk":
            date_format = spidercls.VALID_DATE_FORMATS[spidercls.date_format]
            from_date = datetime.strptime(default_from_date, date_format).replace(tzinfo=timezone.utc)
            kwargs = {"until_date": from_date + timedelta(days=1)}

        # See scrapy.crawler.Crawler._create_spider
        spider = crawler.spidercls.from_crawler(crawler, **kwargs)

        requests = [request async for request in spider.start()]
        assert requests
        for request in requests:
            # See scrapy.core.scraper.Scraper.call_spider
            callback = request.callback or spider.parse

            response = Response("http://example.com", status=555, request=request)
            # If `max_attempts` is set, the spider handles (and retries) error responses.
            if hasattr(spider, "max_attempts"):
                response.request.meta["retries"] = spider.max_attempts
                response.headers["Retry-After"] = 1
            items = list(callback(response))

            assert len(items) == 0
            for record in caplog.records:
                assert re.search(
                    r"^status=555 message='[^']*' request=<(GET|POST) \S+> file_name=\S*$",
                    record.message,
                )
    # Some spiders require API keys.
    except MissingEnvVarError as e:
        pytest.skip(f"{spidercls.name}: {e}")


@pytest.mark.parametrize("spider_name", runner.spider_loader.list())
def test_start_urls_start(spider_name):
    spidercls = runner.spider_loader.load(spider_name)

    assert "start_urls" not in spidercls.__dict__ or "start" not in spidercls.__dict__
