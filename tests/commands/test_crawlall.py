from unittest.mock import patch

import pytest
from scrapy.cmdline import execute


@patch("scrapy.crawler.AsyncCrawlerProcess.start")
@patch("scrapy.crawler.AsyncCrawlerProcess.crawl")
def test_command(crawl, start, caplog):
    with pytest.raises(SystemExit):
        execute(["scrapy", "crawlall", "--dry-run", "--loglevel=WARNING"])

    assert crawl.call_count > 0
    assert start.call_count > 0
    assert len(caplog.records) > 0
