from io import BytesIO

import pytest
from flattentool.input import BadXLSXZipFile
from openpyxl import Workbook
from scrapy.exceptions import NotSupported

from kingfisher_scrapy.items import File
from kingfisher_scrapy.pipelines import Unflatten
from tests import spider_with_crawler


def test_process_item_csv():
    spider = spider_with_crawler(unflatten=True)
    pipeline = Unflatten(spider.crawler)
    item = File(
        file_name="test.csv",
        url="http://test.com/test.csv",
        data_type="release_package",
        data=b"a,b,c\n1,2,3",
    )

    assert pipeline.process_item(item) == item


def test_process_item_xlsx():
    io = BytesIO()
    Workbook().save(io)

    spider = spider_with_crawler(unflatten=True)
    pipeline = Unflatten(spider.crawler)
    item = File(
        file_name="test.xlsx",
        url="http://test.com/test.xlsx",
        data_type="release_package",
        data=io.getvalue(),
    )

    assert pipeline.process_item(item) == item


def test_process_item_extension_error():
    spider = spider_with_crawler(unflatten=True)
    pipeline = Unflatten(spider.crawler)
    item = File(
        file_name="file",
        url="http://test.com/file",
        data_type="release_package",
        data=b"a,b,c\n1,2,3",
    )

    with pytest.raises(NotSupported):
        pipeline.process_item(item)


def test_process_item_xlsx_error():
    spider = spider_with_crawler(unflatten=True)
    pipeline = Unflatten(spider.crawler)
    item = File(
        file_name="test.xlsx",
        url="http://test.com/test.xlsx",
        data_type="release_package",
        data=b"not xlsx data",
    )

    with pytest.raises(BadXLSXZipFile):
        pipeline.process_item(item)
