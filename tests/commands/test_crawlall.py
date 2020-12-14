from unittest.mock import patch

import pytest
from scrapy.cmdline import execute


# tests/extensions/test_kingfisher_process_api.py fails if execute() is already called.
@pytest.mark.order(-1)
@patch('scrapy.crawler.CrawlerProcess.crawl')
def test_command(crawl, caplog):
    with pytest.raises(SystemExit):
        execute(['scrapy', 'crawlall', '--dry-run'])

    assert len(crawl.mock_calls) > 0
    assert len(caplog.records) > 0
