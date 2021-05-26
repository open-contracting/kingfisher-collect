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


@pytest.mark.parametrize('date_format,expected', [
    ('%Y-%m-%dT%H:%M:%S', '2020-01-01T00:00:00'),
    ('%Y-%m-%d', '2020-01-01'),
    ('%Y-%m', '2020-01'),
    ('%Y', '2020'),
])
def test_format_from_date(date_format, expected):
    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00', settings={'DATABASE_URL': 'test',
                                                                             'FILES_STORE': 'test'})
    extension = DatabaseStore.from_crawler(spider.crawler)
    assert extension.format_from_date('2020-01-01T00:00:00', date_format, spider.VALID_DATE_FORMATS) == expected
