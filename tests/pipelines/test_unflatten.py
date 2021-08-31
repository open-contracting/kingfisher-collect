from io import BytesIO

import pytest
from flattentool.input import BadXLSXZipFile
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

from kingfisher_scrapy.items import File
from kingfisher_scrapy.pipelines import Unflatten
from tests import spider_with_crawler


def test_process_item_csv():
    spider = spider_with_crawler(unflatten=True)
    pipeline = Unflatten()
    item = File({
        'file_name': 'test.csv',
        'data': b'data',
        'data_type': 'release_package',
        'url': 'http://test.com/test.csv',
    })

    assert pipeline.process_item(item, spider) == item


def test_process_item_xlsx():
    io = BytesIO()
    Workbook().save(io)

    spider = spider_with_crawler(unflatten=True)
    pipeline = Unflatten()
    item = File({
        'file_name': 'test.xlsx',
        'data': io.getvalue(),
        'data_type': 'release_package',
        'url': 'http://test.com/test.xlsx',
    })

    assert pipeline.process_item(item, spider) == item


def test_process_item_extension_error():
    spider = spider_with_crawler(unflatten=True)
    pipeline = Unflatten()
    item = File({
        'file_name': 'file',
        'data': b'data',
        'data_type': 'release_package',
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
        'data_type': 'release_package',
        'url': 'http://test.com/test.xlsx',
    })

    with pytest.raises(BadXLSXZipFile):
        pipeline.process_item(item, spider)
