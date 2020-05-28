import pytest
from scrapy.http import Request

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.items import File, FileError
from tests import response_fixture, spider_with_crawler


def test_next_link():
    spider = spider_with_crawler(spider_class=LinksSpider)

    request = spider.next_link(response_fixture())

    assert isinstance(request, Request)
    assert request.url == 'http://example.com/next'
    assert request.meta == {'kf_filename': '166715ca8e5f3c1531156d8772b922b7.json'}


def test_parse_404():
    spider = spider_with_crawler(spider_class=LinksSpider)

    generator = spider.parse(response_fixture(status=404))
    item = next(generator)

    assert isinstance(item, FileError)
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

    generator = spider.parse(response_fixture())
    item = next(generator)
    request = next(generator)

    assert isinstance(item, File)
    assert item == {
        'file_name': 'test',
        'url': 'http://example.com',
        'data': b'{"links": {"next": "http://example.com/next"}}',
        'data_type': 'release_package',
        'encoding': 'utf-8',
        'post_to_api': True,
    }

    assert isinstance(request, Request)
    assert request.url == 'http://example.com/next'
    assert request.meta == {'kf_filename': '166715ca8e5f3c1531156d8772b922b7.json'}

    with pytest.raises(StopIteration):
        next(generator)
