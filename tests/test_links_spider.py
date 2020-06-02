import pytest
from scrapy.http import Request

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.items import File, FileError
from tests import response_fixture, spider_with_crawler


def test_next_link():
    spider = spider_with_crawler(spider_class=LinksSpider)
    spider.next_page_formatter = lambda url: 'next.json'

    request = spider.next_link(response_fixture())

    assert type(request) is Request
    assert request.url == 'http://example.com/next'
    assert request.meta == {'kf_filename': 'next.json'}


def test_parse_404():
    spider = spider_with_crawler(spider_class=LinksSpider)

    generator = spider.parse(response_fixture(status=404))
    item = next(generator)

    assert type(item) is FileError
    assert item == {
        'file_name': 'test',
        'url': 'http://example.com',
        'errors': {'http_code': 404},
    }

    with pytest.raises(StopIteration):
        next(generator)


def test_parse_200():
    spider = spider_with_crawler(spider_class=LinksSpider)
    spider.data_type = 'release_package'
    spider.next_page_formatter = lambda url: 'next.json'

    generator = spider.parse(response_fixture())
    item = next(generator)
    request = next(generator)

    assert type(item) is File
    assert item == {
        'file_name': 'test',
        'url': 'http://example.com',
        'data': b'{"links": {"next": "http://example.com/next"}}',
        'data_type': 'release_package',
        'encoding': 'utf-8',
        'post_to_api': True,
    }

    assert type(request) is Request
    assert request.url == 'http://example.com/next'
    assert request.meta == {'kf_filename': 'next.json'}

    with pytest.raises(StopIteration):
        next(generator)
