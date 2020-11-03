import pytest
from flattentool.input import BadXLSXZipFile

from kingfisher_scrapy.items import File
from kingfisher_scrapy.pipelines import Unflatten
from tests import spider_with_crawler


def test_process_item():
    spider = spider_with_crawler(unflatten=True)
    pipeline = Unflatten()
    item = File({
        'file_name': 'test.csv',
        'data': b'data',
        'data_type': 'release_list',
        'url': 'http://test.com/test.csv',
    })

    assert pipeline.process_item(item, spider) == item


def test_process_item_error():
    spider = spider_with_crawler(unflatten=True)
    pipeline = Unflatten()
    item = File({
        'file_name': 'file',
        'data': b'data',
        'data_type': 'release_list',
        'url': 'http://test.com/file',
    })

    with pytest.raises(NotImplementedError):
        pipeline.process_item(item, spider)


def test_process_item_xlsx_error():
    spider = spider_with_crawler(unflatten=True)
    pipeline = Unflatten()
    item = File({
        'file_name': 'test.xlsx',
        'data': b'data',
        'data_type': 'release_list',
        'url': 'http://test.com/test.xlsx',
    })

    with pytest.raises(BadXLSXZipFile):
        pipeline.process_item(item, spider)
