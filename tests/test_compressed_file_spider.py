import json
import os
import pathlib
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import pytest

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.items import File, FileItem
from tests import response_fixture, spider_with_crawler


def test_parse():
    spider = spider_with_crawler(spider_class=CompressedFileSpider)
    spider.data_type = 'release_package'

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', '{}')

    response = response_fixture(body=io.getvalue(), meta={'file_name': 'test.zip'})
    generator = spider.parse(response)
    item = next(generator)

    assert type(item) is File
    assert item == {
        'file_name': 'test.json',
        'url': 'http://example.com',
        'data': b'{}',
        'data_type': 'release_package',
        'encoding': 'utf-8',
        'post_to_api': True,
    }

    with pytest.raises(StopIteration):
        next(generator)


@pytest.mark.parametrize('sample,len_items', [(None, 20), (5, 5)])
def test_parse_json_lines(sample, len_items):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = 'release_package'
    spider.compressed_file_format = 'json_lines'

    content = []
    for i in range(1, 21):
        content.append('{"key": %s}\n' % i)

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', ''.join(content))

    response = response_fixture(body=io.getvalue(), meta={'file_name': 'test.zip'})
    generator = spider.parse(response)
    item = next(generator)
    items = list(generator)

    assert type(item) is File
    assert len(item) == 6
    assert item['file_name'] == 'test.zip'
    assert item['url'] == 'http://example.com'
    assert item['data_type'] == 'zip'
    assert item['encoding'] == 'utf-8'
    assert item['post_to_api'] is False

    assert len(items) == len_items

    for i, item in enumerate(items, 1):
        assert type(item) is FileItem
        assert item == {
            'file_name': 'test.json',
            'url': 'http://example.com',
            'number': i,
            'data': '{"key": %s}\n' % i,
            'data_type': 'release_package',
            'encoding': 'utf-8',
        }


@pytest.mark.parametrize('sample,len_items,len_releases', [(None, 2, 100), (5, 1, 5)])
def test_parse_release_package(sample, len_items, len_releases):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = 'release_package'
    spider.compressed_file_format = 'release_package'

    package = {'releases': []}
    for i in range(200):
        package['releases'].append({'key': 'value'})

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', json.dumps(package))

    response = response_fixture(body=io.getvalue(), meta={'file_name': 'test.zip'})
    generator = spider.parse(response)
    item = next(generator)
    items = list(generator)

    assert type(item) is File
    assert len(item) == 6
    assert item['file_name'] == 'test.zip'
    assert item['url'] == 'http://example.com'
    assert item['data_type'] == 'zip'
    assert item['encoding'] == 'utf-8'
    assert item['post_to_api'] is False

    assert len(items) == len_items
    for i, item in enumerate(items, 1):
        assert type(item) is FileItem
        assert len(item) == 6
        assert item['file_name'] == 'test.json'
        assert item['url'] == 'http://example.com'
        assert item['number'] == i
        assert len(json.loads(item['data'])['releases']) == len_releases
        assert item['data_type'] == 'release_package'
        assert item['encoding'] == 'utf-8'


def test_parse_zip_empty_dir():
    spider = spider_with_crawler(spider_class=CompressedFileSpider)
    spider.data_type = 'release_package'

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        empty_folder = ZipInfo(os.path.join('test', 'test', '/'))
        zipfile.writestr(empty_folder, '')
    response = response_fixture(body=io.getvalue(), meta={'file_name': 'test.zip'})
    generator = spider.parse(response)
    with pytest.raises(StopIteration):
        next(generator)


def test_parse_rar_file():
    spider = spider_with_crawler(spider_class=CompressedFileSpider)
    spider.data_type = 'release_package'

    # the rar library does'nt support the write mode so we use a static rar file
    rar_file_path = os.path.join(pathlib.Path(__file__).parent.absolute(), 'data', 'test.rar')
    with open(rar_file_path, 'rb') as f:
        io = BytesIO(f.read())
    response = response_fixture(body=io.getvalue(), meta={'file_name': 'test.rar'})
    generator = spider.parse(response)
    item = next(generator)

    assert type(item) is File
    assert item == {
        'file_name': 'test.json',
        'url': 'http://example.com',
        'data': b'',
        'data_type': 'release_package',
        'encoding': 'utf-8',
        'post_to_api': True
    }

    with pytest.raises(StopIteration):
        next(generator)
