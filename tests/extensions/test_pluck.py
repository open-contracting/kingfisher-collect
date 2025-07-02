import os
from glob import glob
from tempfile import TemporaryDirectory

import pytest
from scrapy import Request
from scrapy.exceptions import StopDownload

from kingfisher_scrapy.base_spiders import BaseSpider, CompressedFileSpider
from kingfisher_scrapy.extensions import Pluck
from kingfisher_scrapy.items import PluckedItem
from tests import spider_with_crawler


def test_disabled():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(settings={"KINGFISHER_PLUCK_PATH": tmpdirname})
        extension = Pluck.from_crawler(spider.crawler)
        item = PluckedItem(value="2020-10-01")

        extension.item_scraped(item, spider)
        extension.spider_closed(spider, "itemcount")

        assert not glob(os.path.join(tmpdirname, "pluck*.csv"))


def test_item_scraped():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(settings={"KINGFISHER_PLUCK_PATH": tmpdirname}, release_pointer="/date")
        extension = Pluck.from_crawler(spider.crawler)
        item = PluckedItem(value="2020-10-01")

        extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, "pluck-release-date.csv")) as f:
            assert f.read() == "2020-10-01,test\n"

        # Only one item from the same spider is written.
        extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, "pluck-release-date.csv")) as f:
            assert f.read() == "2020-10-01,test\n"


def test_spider_closed_with_items():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(settings={"KINGFISHER_PLUCK_PATH": tmpdirname}, release_pointer="/date")
        extension = Pluck.from_crawler(spider.crawler)
        item = PluckedItem(value="2020-10-01")

        extension.item_scraped(item, spider)
        extension.spider_closed(spider, "itemcount")

        with open(os.path.join(tmpdirname, "pluck-release-date.csv")) as f:
            assert f.read() == "2020-10-01,test\n"


def test_spider_closed_without_items():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(settings={"KINGFISHER_PLUCK_PATH": tmpdirname}, release_pointer="/date")
        extension = Pluck.from_crawler(spider.crawler)

        extension.spider_closed(spider, "itemcount")

        with open(os.path.join(tmpdirname, "pluck-release-date.csv")) as f:
            assert f.read() == "closed: itemcount,test\n"


def test_bytes_received_stop_download():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(
            settings={"KINGFISHER_PLUCK_PATH": tmpdirname, "KINGFISHER_PLUCK_MAX_BYTES": 1}, release_pointer="/date"
        )
        extension = Pluck.from_crawler(spider.crawler)
        request = Request("http://example.com", meta={"file_name": "test.json"})

        with pytest.raises(StopDownload):
            extension.bytes_received(data=b"12345", spider=spider, request=request)

        assert extension.max_bytes == 1


def test_bytes_received_dont_stop_download():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(
            settings={"KINGFISHER_PLUCK_PATH": tmpdirname, "KINGFISHER_PLUCK_MAX_BYTES": 10}, release_pointer="/date"
        )
        extension = Pluck.from_crawler(spider.crawler)
        request = Request("http://example.com", meta={"file_name": "test.json"})

        extension.bytes_received(data=b"12345", spider=spider, request=request)

        assert extension.total_bytes_received == 5
        assert extension.max_bytes == 10


@pytest.mark.parametrize(
    ("test_request", "spider_class", "attributes"),
    [
        (Request("http://example.com", callback=lambda item: item, meta={"file_name": "test.json"}), BaseSpider, {}),
        (Request("http://example.com", meta={"file_name": "test.rar"}), CompressedFileSpider, {}),
        (Request("http://example.com", meta={"file_name": "test.zip"}), CompressedFileSpider, {}),
        (Request("http://example.com", meta={"file_name": "test.xlsx"}), BaseSpider, {"unflatten": True}),
        (Request("http://example.com", meta={"file_name": "test.json"}), BaseSpider, {"root_path": "item"}),
        (Request("http://example.com", meta={"file_name": "test.json"}), BaseSpider, {"dont_truncate": True}),
    ],
)
def test_bytes_received_ignored_requests(test_request, spider_class, attributes):
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_crawler(
            spider_class=spider_class,
            release_pointer="/date",
            settings={"KINGFISHER_PLUCK_PATH": tmpdirname, "KINGFISHER_PLUCK_MAX_BYTES": 10},
        )
        for attr, value in attributes.items():
            setattr(spider, attr, value)

        extension = Pluck.from_crawler(spider.crawler)

        extension.bytes_received(data=b"12345", spider=spider, request=test_request)

        assert extension.total_bytes_received == 0
