import pytest
from flattentool.input import BadXLSXZipFile

from kingfisher_scrapy.base_spider import FlattenSpider
from kingfisher_scrapy.items import File
from tests import response_fixture, spider_with_crawler


def test_parse():
    spider = spider_with_crawler(spider_class=FlattenSpider)
    spider.data_type = 'release'

    generator = spider.parse(response_fixture(url_path='/example/file.csv'))
    csv_item = next(generator)
    json_item = next(generator)

    assert type(csv_item) is File
    assert csv_item == {
        'data': b'{"links": {"next": "http://example.com/next"}}',
        'data_type': 'release',
        'encoding': 'utf-8',
        'file_name': 'file.csv',
        'post_to_api': False,
        'url': 'http://example.com/example/file.csv'
    }

    assert type(json_item) is File
    assert json_item == {
        'data': '{\n    "releases": []\n}',
        'data_type': 'release',
        'encoding': 'utf-8',
        'file_name': 'test',
        'post_to_api': True,
        'url': 'http://example.com/example/file.csv'
    }


def test_xlsx_file_error():
    spider = spider_with_crawler(spider_class=FlattenSpider)
    spider.data_type = 'release'

    generator = spider.parse(response_fixture(url_path='/example/file.xlsx'))
    item = next(generator)

    assert type(item) is File
    assert item == {
        'data': b'{"links": {"next": "http://example.com/next"}}',
        'data_type': 'release',
        'encoding': 'utf-8',
        'file_name': 'file.xlsx',
        'post_to_api': False,
        'url': 'http://example.com/example/file.xlsx'
    }

    with pytest.raises(BadXLSXZipFile) as e:
        next(generator)
    assert str(e.value) == "The supplied file has extension .xlsx but isn't an XLSX file."


def test_extension_error():
    spider = spider_with_crawler(spider_class=FlattenSpider)
    spider.data_type = 'release'

    generator = spider.parse(response_fixture(url_path='/example/file'))
    item = next(generator)

    assert item == {
        'errors': {
            'detail': 'The file has no extension or is not CSV or XLSX',
            'http_code': 400
        },
        'file_name': 'file',
        'url': 'http://example.com/example/file'
    }
