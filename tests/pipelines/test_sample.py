from unittest.mock import MagicMock

import pytest
from scrapy.exceptions import DropItem

from kingfisher_scrapy.items import File, FileError
from kingfisher_scrapy.pipelines import Sample
from tests import spider_with_crawler


def test_process_file_without_sample():
    pipeline = Sample()
    spider = spider_with_crawler()
    item = File(
        file_name='test',
        url='http://test.com',
        data_type='release_package',
        data=b'{}',
    )
    assert pipeline.process_item(item, spider) == item


def test_process_file_with_sample():
    pipeline = Sample()
    spider = spider_with_crawler(sample=1)
    crawler = MagicMock()
    spider.crawler = crawler
    item = File(
        file_name='test',
        url='http://test.com',
        data_type='release_package',
        data=b'{}',
    )
    assert pipeline.process_item(item, spider) == item
    with pytest.raises(DropItem):
        pipeline.process_item(item, spider)


def test_process_item_file_error():
    pipeline = Sample()
    spider = spider_with_crawler(sample=1)
    item = FileError(
        file_name='test',
        url='http://test.com',
        errors={'http_code': 500},
    )
    with pytest.raises(DropItem):
        pipeline.process_item(item, spider)
