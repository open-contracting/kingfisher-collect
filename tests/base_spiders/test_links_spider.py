import datetime

import pytest
from scrapy.http import Request
from scrapy.utils.trackref import NoneType

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.exceptions import MissingNextLinkError
from kingfisher_scrapy.items import File
from tests import response_fixture, spider_with_crawler


def test_next_link():
    spider = spider_with_crawler(spider_class=LinksSpider)
    spider.formatter = lambda _url: "next.json"

    request = spider.next_link(
        response_fixture(
            meta={"file_name": "test", "depth": 0},
            body=b'{"links": {"next": "http://example.com/next"}}',
        ),
    )

    assert type(request) is Request
    assert request.url == "http://example.com/next"
    assert request.meta == {"file_name": "next.json"}


def test_next_link_condition():
    spider = spider_with_crawler(spider_class=LinksSpider)
    spider.from_date = spider.until_date = datetime.date(2002, 12, 31)

    request = spider.next_link(
        response_fixture(
            meta={"file_name": "test", "depth": 0},
            body='{"links": {"next": ""}}',
        ),
    )

    assert type(request) is NoneType


def test_parse_404(caplog):
    spider = spider_with_crawler(spider_class=LinksSpider)

    generator = spider.parse(
        response_fixture(
            meta={"file_name": "test", "depth": 0},
            body=b'{"links": {"next": "http://example.com/next"}}',
            status=404,
        ),
    )

    assert len(list(generator)) == 0
    assert [record.message for record in caplog.records] == [
        "status=404 message='' request=<GET http://example.com> file_name=test"
    ]


def test_parse_200():
    spider = spider_with_crawler(spider_class=LinksSpider)
    spider.data_type = "release_package"
    spider.formatter = lambda _url: "next.json"
    body = b'{"links": {"next": "http://example.com/next"}}'

    generator = spider.parse(response_fixture(meta={"file_name": "test", "depth": 0}, body=body))
    item = next(generator)
    request = next(generator)

    assert type(item) is File
    assert item.model_dump() == {
        "file_name": "test",
        "url": "http://example.com/",
        "data_type": "release_package",
        "data": body,
        "path": "",
    }

    assert type(request) is Request
    assert request.url == "http://example.com/next"
    assert request.meta == {"file_name": "next.json"}

    with pytest.raises(StopIteration):
        next(generator)


def test_next_link_not_found_first_page():
    spider = spider_with_crawler(spider_class=LinksSpider)
    spider.filter_arguments = []
    body = '{"links": {"next": ""}}'

    meta = {"file_name": "test", "depth": 0}
    with pytest.raises(MissingNextLinkError) as e:
        spider.next_link(response_fixture(body=body, meta=meta))
    assert str(e.value) == "Missing link on first page, ending crawl prematurely: http://example.com"

    meta = {"file_name": "test", "depth": 10}
    response = spider.next_link(response_fixture(body=body, meta=meta))
    assert response is None


def test_next_link_not_found_later_page():
    spider = spider_with_crawler(spider_class=LinksSpider)
    spider.filter_arguments = []
    body = '{"value": 000}'

    meta = {"file_name": "test", "depth": 4}
    with pytest.raises(MissingNextLinkError) as e:
        spider.next_link(response_fixture(body=body, meta=meta))
    assert str(e.value) == "Invalid JSON on page 4, ending crawl prematurely: http://example.com"
