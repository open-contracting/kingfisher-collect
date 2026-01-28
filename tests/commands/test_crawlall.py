from unittest.mock import patch

import pytest
from scrapy.cmdline import execute


@patch("scrapy.crawler.CrawlerProcess.crawl")
def test_command(crawl, caplog):
    with pytest.raises(SystemExit):
        execute(["scrapy", "crawlall", "--dry-run"])

    assert crawl.call_count > 0
    assert len(caplog.records) > 0
