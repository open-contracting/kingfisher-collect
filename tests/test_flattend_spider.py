import pytest
from click import File
from flattentool.input import BadXLSXZipFile

from kingfisher_scrapy.base_spider import FlattenSpider
from kingfisher_scrapy.exceptions import SpreadsheetExtensionError
from kingfisher_scrapy.items import File
from tests import response_fixture, spider_with_crawler


def test_parse():
    spider = spider_with_crawler(spider_class=FlattenSpider)
    spider.data_type = 'release'

    generator = spider.parse(response_fixture(url_path='/example/file.csv'))
    item = next(generator)

    assert type(item) is File
    assert item == {
        'data': '{\n    "releases": []\n}',
        'data_type': 'release',
        'encoding': 'utf-8',
        'file_name': 'test',
        'post_to_api': True,
        'url': 'http://example.com/example/file.csv'
    }


def test_xlsx_file_error():
    spider = spider_with_crawler(spider_class=FlattenSpider)

    generator = spider.parse(response_fixture(url_path='/example/file.xlsx'))
    with pytest.raises(BadXLSXZipFile) as e:
        next(generator)
    assert str(e.value) == "The supplied file has extension .xlsx but isn't an XLSX file."


def test_spreadsheet_extension_error():
    spider = spider_with_crawler(spider_class=FlattenSpider)

    generator = spider.parse(response_fixture(url_path='/example/file'))
    with pytest.raises(SpreadsheetExtensionError) as e:
        next(generator)
    assert str(e.value) == 'The file has no extension or is not CSV or XLSX.'
