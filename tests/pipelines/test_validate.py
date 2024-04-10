import pytest
from jsonschema import ValidationError
from scrapy.exceptions import DropItem

from kingfisher_scrapy.items import File, FileError, FileItem
from kingfisher_scrapy.pipelines import Validate
from tests import spider_with_crawler


def test_process_item():
    pipeline = Validate()
    item = File(
        file_name='test',
        url='http://test.com',
        data_type='release_package',
        data='data',
    )

    assert pipeline.process_item(item, None) == item

    item.data = item.data.encode('ascii')
    item.file_name = 'test2'

    assert pipeline.process_item(item, None) == item


def test_process_item_error():
    pipeline = Validate()

    with pytest.raises(TypeError):
        File(
            url='http://test.com',
            data_type='release_package',
            data='data',
        )

    item = File(
        file_name='test',
        url='http://test.com',
        data_type='not a valid data type',
        data='data',
    )

    with pytest.raises(ValidationError):
        pipeline.process_item(item, None)


def test_process_file_item():
    pipeline = Validate()
    item = FileItem(
        file_name='test',
        url='http://test.com',
        data_type='release_package',
        data='data',
        number=1,
    )
    assert pipeline.process_item(item, None) == item


def test_process_file_item_error():
    pipeline = Validate()
    item = FileItem(
        file_name='test',
        url='http://test.com',
        data_type='release_package',
        data='data',
        number='2',
    )
    with pytest.raises(ValidationError):
        pipeline.process_item(item, None)
    item.number = None
    with pytest.raises(ValidationError):
        pipeline.process_item(item, None)


def test_process_file_error():
    pipeline = Validate()
    item = FileError(
        file_name='test',
        url='http://test.com',
        errors={'http_code': 500},
    )
    assert pipeline.process_item(item, None) == item


def test_process_file_item_error_error():
    pipeline = Validate()

    with pytest.raises(TypeError):
        FileError(
            file_name='test',
            url='http://test.com',
        )

    item = FileError(
        file_name='test',
        url='not an url',
        errors={'http_code': 500},
    )

    with pytest.raises(ValidationError):
        pipeline.process_item(item, None)


def test_process_item_duplicate_file(caplog):
    pipeline = Validate()
    spider = spider_with_crawler()
    item = File(
        file_name='test1',
        url='http://example.com',
        data_type='release_package',
        data='data',
    )

    pipeline.process_item(item, spider)
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item, spider)

    item2 = File(
        file_name='file2',
        url='http://example.com',
        data_type='release_package',
        data='data',
    )
    pipeline.process_item(item2, spider)

    assert str(excinfo.value) == "Duplicate File: 'test1'"


def test_process_item_duplicate_file_item(caplog):
    pipeline = Validate()
    spider = spider_with_crawler()
    item = FileItem(
        file_name='test1',
        url='http://example.com',
        data_type='release_package',
        data='data',
        number=1,
    )

    pipeline.process_item(item, spider)
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item, spider)

    item2 = FileItem(
        file_name='test1',
        url='http://example.com',
        data_type='release_package',
        data='data',
        number=2,
    )
    pipeline.process_item(item2, spider)

    assert str(excinfo.value) == "Duplicate FileItem: ('test1', 1)"
