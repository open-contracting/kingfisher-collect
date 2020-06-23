import pytest

from kingfisher_scrapy.exceptions import MissingRequiredFieldError
from kingfisher_scrapy.items import File, FileItem
from kingfisher_scrapy.pipelines import Validate
from tests import spider_with_crawler


def test_process_item():
    pipeline = Validate()
    item = File({
        'file_name': '',
        'data': '',
        'data_type': '',
        'url': '',
    })

    assert pipeline.process_item(item, None) == item


def test_process_item_error():
    pipeline = Validate()
    item = File()

    with pytest.raises(MissingRequiredFieldError):
        pipeline.process_item(item, None)


def test_duplicate_file(caplog):
    pipeline = Validate()
    spider = spider_with_crawler()
    item = File({
        'file_name': 'test1',
        'data': '',
        'data_type': '',
        'url': '',
    })

    pipeline.process_item(item, spider)
    pipeline.process_item(item, spider)
    item2 = item.copy()
    item2['file_name'] = 'file2'
    pipeline.process_item(item2, spider)

    assert len(caplog.messages) == 1
    assert caplog.messages[0] == "Duplicate File: 'test1'"


def test_duplicate_file_item(caplog):
    pipeline = Validate()
    spider = spider_with_crawler()
    item = FileItem({
        'file_name': 'test1',
        'data': '',
        'data_type': '',
        'url': '',
        'number': 1
    })

    pipeline.process_item(item, spider)
    pipeline.process_item(item, spider)
    item2 = item.copy()
    item2['number'] = 2
    pipeline.process_item(item2, spider)

    assert len(caplog.messages) == 1
    assert caplog.messages[0] == "Duplicate FileItem: ('test1', 1)"
