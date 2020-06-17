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


def test_duplicated_filename(caplog):
    pipeline = Validate()
    spider = spider_with_crawler()
    item = File({
        'file_name': 'test1',
        'data': '',
        'data_type': '',
        'url': '',
    })
    assert pipeline.process_item(item, spider) == item
    pipeline.process_item(item, spider)
    assert caplog.messages[0] == 'Duplicated filename: test1'
    assert len(pipeline.file_names) == 1
    item2 = item.copy()
    item2['file_name'] = 'file2'
    pipeline.process_item(item2, spider)
    assert len(pipeline.file_names) == 2


def test_duplicated_fileitem(caplog):
    pipeline = Validate()
    spider = spider_with_crawler()
    item = FileItem({
        'file_name': 'test1',
        'data': '',
        'data_type': '',
        'url': '',
        'number': 1
    })
    assert pipeline.process_item(item, spider) == item
    pipeline.process_item(item, spider)
    assert caplog.messages[0] == 'Duplicated filename and number pair: test1-1'
    assert len(pipeline.file_items) == 1
    item2 = item.copy()
    item2['number'] = 2
    pipeline.process_item(item2, spider)
    assert len(pipeline.file_items) == 2
