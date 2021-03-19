import pytest
from jsonschema import ValidationError
from scrapy.exceptions import DropItem

from kingfisher_scrapy.items import File, FileError, FileItem
from kingfisher_scrapy.pipelines import Validate
from tests import spider_with_crawler


def test_process_item():
    pipeline = Validate()
    item = File({
        'file_name': 'test',
        'data': 'data',
        'data_type': 'release_package',
        'url': 'http://test.com',
    })

    assert pipeline.process_item(item, None) == item

    item['data'] = item['data'].encode('ascii')
    item['file_name'] = 'test2'

    assert pipeline.process_item(item, None) == item


def test_process_item_error():
    pipeline = Validate()
    item = File({
        'data': 'data',
        'data_type': 'release_package',
        'url': 'http://test.com',
    })

    with pytest.raises(ValidationError):
        pipeline.process_item(item, None)
    item['file_name'] = 'test'
    item['data_type'] = 'not a valid data type'
    with pytest.raises(ValidationError):
        pipeline.process_item(item, None)


def test_process_file_item():
    pipeline = Validate()
    item = FileItem({
        'file_name': 'test',
        'data': 'data',
        'data_type': 'release_package',
        'url': 'http://test.com',
        'number': 1
    })
    assert pipeline.process_item(item, None) == item


def test_process_file_item_error():
    pipeline = Validate()
    item = FileItem({
        'file_name': 'test',
        'data': 'data',
        'data_type': 'release_package',
        'url': 'http://test.com',
        'number': "2"
    })
    with pytest.raises(ValidationError):
        pipeline.process_item(item, None)
    item['number'] = None
    with pytest.raises(ValidationError):
        pipeline.process_item(item, None)


def test_process_file_error():
    pipeline = Validate()
    item = FileError({
        'file_name': 'test',
        'url': 'http://test.com',
        'errors': 'Error'
    })
    assert pipeline.process_item(item, None) == item


def test_process_file_item_error_error():
    pipeline = Validate()
    item = FileError({
        'file_name': 'test',
        'url': 'http://test.com'
    })
    with pytest.raises(ValidationError):
        pipeline.process_item(item, None)
    item['errors'] = 'Error'
    item['url'] = 'not an url'
    with pytest.raises(ValidationError):
        pipeline.process_item(item, None)


def test_process_item_duplicate_file(caplog):
    pipeline = Validate()
    spider = spider_with_crawler()
    item = File({
        'file_name': 'test1',
        'data': 'data',
        'data_type': 'release_package',
        'url': 'http://example.com',
    })

    pipeline.process_item(item, spider)
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item, spider)
    assert str(excinfo.value) == "Duplicate File: test1"


def test_process_item_duplicate_file_item(caplog):
    pipeline = Validate()
    spider = spider_with_crawler()
    item = FileItem({
        'file_name': 'test1',
        'data': 'data',
        'data_type': 'release_package',
        'url': 'http://example.com',
        'number': 1
    })

    pipeline.process_item(item, spider)
    with pytest.raises(DropItem) as excinfo:
        pipeline.process_item(item, spider)
    assert str(excinfo.value) == "Duplicate File Item: test1-1"
