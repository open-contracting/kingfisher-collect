import json
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from kingfisher_scrapy.base_spider import CompressedFileSpider, SimpleSpider
from kingfisher_scrapy.items import File, FileError, FileItem
from kingfisher_scrapy.middlewares import (AddPackageMiddleware, LineDelimitedMiddleware, ReadDataMiddleware,
                                           ResizePackageMiddleware, RootPathMiddleware, ConcatenatedJSONMiddleware)
from tests import response_fixture, spider_with_crawler


@pytest.mark.parametrize('middleware_class', [
    AddPackageMiddleware,
    LineDelimitedMiddleware,
    ResizePackageMiddleware,
    RootPathMiddleware,
    ReadDataMiddleware,
])
@pytest.mark.parametrize('item', [
    File({
        'file_name': 'test',
        'data': 'data',
        'data_type': 'release_package',
        'url': 'http://test.com',
    }),
    FileError({
        'file_name': 'test',
        'url': 'http://test.com',
        'errors': ''
    }),
])
def test_yield_items(middleware_class, item):
    spider = spider_with_crawler()

    middleware = middleware_class()

    generator = middleware.process_spider_output(None, [item], spider)
    returned_item = next(generator)

    assert item == returned_item


@pytest.mark.parametrize('data_type,data,root_path', [
    ('release', b'{"ocid": "abc"}', ''),
    ('record', b'{"ocid": "abc"}', ''),
    ('release', b'[{"ocid": "abc"}]', 'item'),
    ('record', b'[{"ocid": "abc"}]', 'item'),
    ('release', b'{"results":[{"ocid": "abc"}]}', 'results.item'),
    ('record', b'{"results":[{"ocid": "abc"}]}', 'results.item'),
    ('release_package', b'[{"releases":[{"ocid": "abc"}], "uri": "test"}]', 'item'),
    ('record_package', b'[{"records":[{"ocid": "abc"}], "uri": "test"}]', 'item'),
])
def test_data_types(data_type, data, root_path):
    spider = spider_with_crawler()
    spider.root_path = root_path

    root_path_middleware = RootPathMiddleware()
    add_package_middleware = AddPackageMiddleware()

    item = File({
        'file_name': 'test',
        'data': data,
        'data_type': data_type,
        'url': 'http://test.com',
        'encoding': 'utf-8'
    })

    generator = root_path_middleware.process_spider_output(None, [item], spider)
    item = next(generator)
    generator = add_package_middleware.process_spider_output(None, [item], spider)
    item = next(generator)

    expected = {
        'file_name': 'test',
        'url': 'http://test.com',
        'encoding': 'utf-8',
    }
    if root_path:
        expected['number'] = 1

    if 'package' in data_type:
        expected['data'] = {f"{data_type[:-8]}s": [{"ocid": "abc"}], "uri": "test"}
        expected['data_type'] = data_type
    else:
        expected['data'] = {f"{data_type}s": [{"ocid": "abc"}], "version": spider.ocds_version}
        expected['data_type'] = f'{data_type}_package'

    assert item == expected


@pytest.mark.parametrize('sample,len_releases,file_name', [(None, 100, 'test'), (5, 5, 'test')])
def test_parse_release_package(sample, len_releases, file_name):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = 'release_package'
    spider.resize_package = True

    middleware = ResizePackageMiddleware()

    package = {'releases': []}
    for i in range(200):
        package['releases'].append({'key': 'value'})

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', json.dumps(package))

    response = response_fixture(body=io.getvalue(), meta={'file_name': f'{file_name}.zip'})
    generator = spider.parse(response)
    item = next(generator)

    generator = middleware.process_spider_output(response, [item], spider)
    transformed_items = list(generator)

    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        assert len(item) == 6
        assert item['file_name'] == f'{file_name}-test.json'
        assert item['url'] == 'http://example.com'
        assert item['number'] == i
        assert len(json.loads(item['data'])['releases']) == len_releases
        assert item['data_type'] == 'release_package'
        assert item['encoding'] == 'utf-8'


@pytest.mark.parametrize('delimited_type', ['line', 'concatenated'])
@pytest.mark.parametrize('sample', [None, 5])
def test_custom_delimited_json_middleware(sample, delimited_type):
    spider = spider_with_crawler(spider_class=SimpleSpider, sample=sample)
    spider.data_type = 'release_package'
    if delimited_type == 'line':
        spider.line_delimited = True
        middleware = LineDelimitedMiddleware()
        separator = '\n'
    else:
        spider.concatenated_json = True
        middleware = ConcatenatedJSONMiddleware()
        separator = ''

    content = []
    for i in range(1, 21):
        content.append('{"key": %s}%s' % (i, separator))

    response = response_fixture(body=''.join(content), meta={'file_name': 'test.json'})
    generator = spider.parse(response)
    item = next(generator)

    generator = middleware.process_spider_output(response, [item], spider)
    transformed_items = list(generator)

    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        if delimited_type == 'concatenated':
            data = {'key': i}
        else:
            data = '{"key": %s}\n' % i
        assert item == {
            'file_name': 'test.json',
            'url': 'http://example.com',
            'number': i,
            'data': data,
            'data_type': 'release_package',
            'encoding': 'utf-8'
        }


@pytest.mark.parametrize('sample', [None, 5])
def test_line_delimited_json_middleware_compressed(sample):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = 'release_package'
    spider.line_delimited = True

    middleware = LineDelimitedMiddleware()

    content = []
    for i in range(1, 21):
        content.append('{"key": %s}\n' % i)

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', ''.join(content))

    response = response_fixture(body=io.getvalue(), meta={'file_name': 'test.zip'})
    generator = spider.parse(response)
    item = next(generator)

    generator = middleware.process_spider_output(response, [item], spider)
    transformed_items = list(generator)

    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        assert item == {
            'file_name': 'test-test.json',
            'url': 'http://example.com',
            'number': i,
            'data': '{"key": %s}\n' % i,
            'data_type': 'release_package',
            'encoding': 'utf-8'
        }


def test_read_decompressed_middleware():
    spider = spider_with_crawler(spider_class=CompressedFileSpider)
    spider.data_type = 'release_package'

    middleware = ReadDataMiddleware()

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', '{}')

    response = response_fixture(body=io.getvalue(), meta={'file_name': 'test.zip'})
    generator = spider.parse(response)
    item = next(generator)

    generator = middleware.process_spider_output(response, [item], spider)
    transformed_items = list(generator)

    assert len(transformed_items) == 1
    assert transformed_items[0]['data'] == b'{}'
