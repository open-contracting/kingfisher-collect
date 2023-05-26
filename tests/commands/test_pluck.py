from unittest.mock import patch

import pytest
from scrapy.cmdline import execute


# tests/extensions/test_kingfisher_process_api.py fails if execute() is already called.
@pytest.mark.order(-1)
@patch('scrapy.crawler.CrawlerProcess.crawl')
def test_command(crawl, caplog):
    with pytest.raises(SystemExit):
        execute(['scrapy', 'pluck', '--release-pointer', '/date'])

    assert crawl.call_count > 0
    assert len(caplog.records) > 0
