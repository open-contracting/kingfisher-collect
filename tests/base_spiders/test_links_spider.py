from datetime import date

import pytest
from scrapy.http import Request
from scrapy.utils.trackref import NoneType

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.exceptions import MissingNextLinkError
from kingfisher_scrapy.items import File, FileError
from tests import response_fixture, spider_with_crawler


def test_next_link():
    spider = spider_with_crawler(spider_class=LinksSpider)
    spider.formatter = lambda url: 'next.json'

    request = spider.next_link(response_fixture(body=b'{"links": {"next": "http://example.com/next"}}'))

    assert type(request) is Request
    assert request.url == 'http://example.com/next'
    assert request.meta == {'file_name': 'next.json'}


def test_next_link_condition():
    spider = spider_with_crawler(spider_class=LinksSpider)
    spider.from_date = spider.until_date = date(2002, 12, 31)

    request = spider.next_link(response_fixture(body='{"links": {"next": ""}}'))

    assert type(request) is NoneType


def test_parse_404():
    spider = spider_with_crawler(spider_class=LinksSpider)

    generator = spider.parse(response_fixture(status=404, body=b'{"links": {"next": "http://example.com/next"}}'))
    item = next(generator)

    assert type(item) is FileError
    assert item.__dict__ == {
        'file_name': 'test',
        'url': 'http://example.com',
        'errors': {'http_code': 404},
    }

    with pytest.raises(StopIteration):
        next(generator)


def test_parse_200():
    spider = spider_with_crawler(spider_class=LinksSpider)
    spider.data_type = 'release_package'
    spider.formatter = lambda url: 'next.json'
    body = b'{"links": {"next": "http://example.com/next"}}'

    generator = spider.parse(response_fixture(body=body))
    item = next(generator)
    request = next(generator)

    assert type(item) is File
    assert item.__dict__ == {
        'file_name': 'test',
        'url': 'http://example.com',
        'data_type': 'release_package',
        'data': body,
        'path': '',
    }

    assert type(request) is Request
    assert request.url == 'http://example.com/next'
    assert request.meta == {'file_name': 'next.json'}

    with pytest.raises(StopIteration):
        next(generator)


def test_next_link_not_found():
    spider = spider_with_crawler(spider_class=LinksSpider)
    spider.filter_arguments = []
    body = '{"links": {"next": ""}}'

    with pytest.raises(MissingNextLinkError) as e:
        meta = {'file_name': 'test', 'depth': 0}
        spider.next_link(response_fixture(meta=meta, body=body))
    assert str(e.value) == 'next link not found on the first page: http://example.com'

    meta = {'file_name': 'test', 'depth': 10}
    response = spider.next_link(response_fixture(meta=meta, body=body))
    assert response is None
