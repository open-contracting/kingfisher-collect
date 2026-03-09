import datetime

import pytest
from scrapy.crawler import Crawler, CrawlerRunner
from scrapy.utils.project import get_project_settings

from kingfisher_scrapy.exceptions import MissingEnvVarError

# See scrapy.cmdline.execute
settings = get_project_settings()
runner = CrawlerRunner(settings)


# See scrapy.commands.list
@pytest.mark.parametrize("spider_name", runner.spider_loader.list())
async def test_start_requests(spider_name):
    # See scrapy.crawler.CrawlerRunner._create_crawler
    spidercls = runner.spider_loader.load(spider_name)
    crawler = Crawler(spidercls, runner.settings)
    crawler._apply_settings()  # noqa: SLF001

    # CoreStats.spider_opened
    crawler.stats.set_value("start_time", datetime.datetime(2001, 2, 3, 4, 5, 6))

    try:
        kwargs = {}
        if default_from_date := getattr(spidercls, "default_from_date", None):
            from_date = datetime.datetime.strptime(
                default_from_date, spidercls.VALID_DATE_FORMATS[spidercls.date_format]
            ).replace(tzinfo=datetime.timezone.utc)
            kwargs = {"until_date": from_date + datetime.timedelta(days=1)}

        # See scrapy.crawler.Crawler._create_spider
        spider = crawler.spidercls.from_crawler(crawler, **kwargs)

        assert [request async for request in spider.start()]
    # Some spiders require API keys.
    except MissingEnvVarError as e:
        pytest.skip(f"{spidercls.name}: {e}")


@pytest.mark.parametrize("spider_name", runner.spider_loader.list())
def test_start_urls_start(spider_name):
    spidercls = runner.spider_loader.load(spider_name)

    assert "start_urls" not in spidercls.__dict__ or "start" not in spidercls.__dict__
