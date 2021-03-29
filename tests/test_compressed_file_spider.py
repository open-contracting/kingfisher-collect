import json
import os
import pathlib
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import pytest

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.items import File
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
    assert item['file_name'] == 'test-test.json'
    assert item['url'] == 'http://example.com'
    assert item['data_type'] == 'release_package'
    assert item['encoding'] == 'utf-8'
    assert item['data'] is not None
    assert 'package' not in item['data']

    with pytest.raises(StopIteration):
        next(generator)


@pytest.mark.parametrize('sample,len_items,file_name', [(None, 20, 'test'), (5, 5, 'test')])
def test_parse_line_delimited(sample, len_items, file_name):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = 'release_package'
    spider.line_delimited = True

    content = []
    for i in range(1, 21):
        content.append('{"key": %s}\n' % i)

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', ''.join(content))

    response = response_fixture(body=io.getvalue(), meta={'file_name': f'{file_name}.zip'})
    generator = spider.parse(response)
    item = next(generator)

    assert type(item) is File
    assert len(item) == 5
    assert item['file_name'] == f'{file_name}-test.json'
    assert item['url'] == 'http://example.com'
    assert item['data_type'] == 'release_package'
    assert item['encoding'] == 'utf-8'
    assert item['data'] is not None
    assert 'package' not in item['data']

    with pytest.raises(StopIteration):
        next(generator)


@pytest.mark.parametrize('sample,len_items,len_releases, file_name', [(None, 2, 100, 'test'), (5, 1, 5, 'test')])
def test_parse_release_package(sample, len_items, len_releases, file_name):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = 'release_package'
    spider.resize_package = True

    package = {'releases': []}
    for i in range(200):
        package['releases'].append({'key': 'value'})

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', json.dumps(package))

    response = response_fixture(body=io.getvalue(), meta={'file_name': f'{file_name}.zip'})
    generator = spider.parse(response)
    item = next(generator)

    assert type(item) is File
    assert len(item) == 5
    assert item['file_name'] == f'{file_name}-test.json'
    assert item['url'] == 'http://example.com'
    assert item['data_type'] == 'release_package'
    assert item['encoding'] == 'utf-8'
    assert item['data']['package'] is not None
    assert item['data']['data'] is not None

    with pytest.raises(StopIteration):
        next(generator)


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
    assert len(item) == 5
    assert item['file_name'] == 'test-test.json'
    assert item['url'] == 'http://example.com'
    assert item['data_type'] == 'release_package'
    assert item['encoding'] == 'utf-8'
    assert item['data'] is not None
    assert 'package' not in item['data']

    with pytest.raises(StopIteration):
        next(generator)
