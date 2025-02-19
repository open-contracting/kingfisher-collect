import pytest
from scrapy.exceptions import DropItem

from kingfisher_scrapy.items import File, FileItem
from kingfisher_scrapy.pipelines import Validate
from tests import spider_with_crawler


def test_process_item_with_file():
    pipeline = Validate()
    item = File(
        file_name='test',
        url='http://test.com',
        data_type='release_package',
        data=b'{}',
    )

    assert pipeline.process_item(item, None) == item

    item.file_name = 'test2'

    assert pipeline.process_item(item, None) == item


def test_process_item_with_file_item():
    pipeline = Validate()
    item = FileItem(
        file_name='test',
        url='http://test.com',
        data_type='release_package',
        data=b'{}',
        number=1,
    )

    assert pipeline.process_item(item, None) == item

    item.number = 2

    assert pipeline.process_item(item, None) == item


def test_process_item_with_duplicate_file(caplog):
    pipeline = Validate()
    spider = spider_with_crawler()
    item = File(
        file_name='test1',
        url='http://example.com',
        data_type='release_package',
        data=b'{}',
    )

    pipeline.process_item(item, spider)
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item, spider)

    item2 = File(
        file_name='file2',
        url='http://example.com',
        data_type='release_package',
        data=b'{}',
    )
    pipeline.process_item(item2, spider)

    assert str(excinfo.value) == "Duplicate File: 'test1'"


def test_process_item_with_duplicate_file_item(caplog):
    pipeline = Validate()
    spider = spider_with_crawler()
    item = FileItem(
        file_name='test1',
        url='http://example.com',
        data_type='release_package',
        data=b'{}',
        number=1,
    )

    pipeline.process_item(item, spider)
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item, spider)

    item2 = FileItem(
        file_name='test1',
        url='http://example.com',
        data_type='release_package',
        data=b'{}',
        number=2,
    )
    pipeline.process_item(item2, spider)

    assert str(excinfo.value) == "Duplicate FileItem: ('test1', 1)"
