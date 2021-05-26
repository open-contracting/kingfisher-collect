import pytest
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.extensions import DatabaseStore
from tests import spider_with_crawler


def test_from_crawler_missing_arguments():
    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00')

    with pytest.raises(NotConfigured) as excinfo:
        DatabaseStore.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'DATABASE_URL is not set.'

    spider.crawler.settings = {'DATABASE_URL': 'test', 'FILES_STORE': None}
    with pytest.raises(NotConfigured) as excinfo:
        DatabaseStore.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'FILES_STORE is not set.'
