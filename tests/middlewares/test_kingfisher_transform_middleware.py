import json
from io import BytesIO
from unittest.mock import MagicMock
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from kingfisher_scrapy.base_spider import CompressedFileSpider, SimpleSpider
from kingfisher_scrapy.items import File, FileError, FileItem
from kingfisher_scrapy.middlewares import (
    KingfisherTransformAddPackageMiddleware,
    KingfisherTransformLineDelimitedJSONMiddleware,
    KingfisherTransformResizePackageMiddleware,
    KingfisherTransformRootPathMiddleware)
from tests import response_fixture, spider_with_crawler


@pytest.mark.parametrize('middleware', [
    KingfisherTransformAddPackageMiddleware,
    KingfisherTransformLineDelimitedJSONMiddleware,
    KingfisherTransformResizePackageMiddleware,
    KingfisherTransformRootPathMiddleware,
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
def test_yield_items(middleware, item):
    spider = spider_with_crawler()
    transform_middleware = middleware()
    generator = transform_middleware.process_spider_output(None, [item], spider)
    returned_item = next(generator)

    assert item == returned_item


@pytest.mark.parametrize('data_type,data,root_path', [
    ('release', b'{"ocid": "abc"}', ''),
    ('record', b'{"ocid": "abc"}', ''),
    ('record', b'[{"ocid": "abc"}]', 'item'),
    ('release', b'[{"ocid": "abc"}]', 'item'),
    ('release', b'{"results":[{"ocid": "abc"}]}', 'results.item'),
    ('record', b'{"results":[{"ocid": "abc"}]}', 'results.item'),
    ('release_package', b'[{"releases":[{"ocid": "abc"}], "uri": "test"}]', 'item'),
    ('record_package', b'[{"records":[{"ocid": "abc"}], "uri": "test"}]', 'item'),
])
def test_data_types(data_type, data, root_path):
    spider = spider_with_crawler()
    spider.root_path = root_path

    root_path_middleware = KingfisherTransformRootPathMiddleware()
    add_package_middleware = KingfisherTransformAddPackageMiddleware()

    item = File({
        'file_name': 'test',
        'data': data,
        'data_type': data_type,
        'url': 'http://test.com',
        'encoding': 'utf-8'
    })
    response_mock = MagicMock()

    response_mock.request.url = item['url']
    generator = root_path_middleware.process_spider_output(response_mock, [item], spider)
    returned_item = next(generator)

    response_mock['data'] = returned_item
    generator = add_package_middleware.process_spider_output(response_mock, [item], spider)
    returned_item = next(generator)

    if 'package' in data_type:
        assert returned_item['data_type'] == data_type
        assert returned_item['data'] == {f"{data_type[:-8]}s": [{"ocid": "abc"}], "uri": "test"}
    else:
        assert returned_item['data_type'] == f'{data_type}_package'
        assert returned_item['data'] == {f"{data_type}s": [{"ocid": "abc"}]}


@pytest.mark.parametrize('sample,len_releases', [(None, 100), (5, 5)])
def test_parse_release_package(sample, len_releases):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = 'release_package'
    spider.compressed_file_format = 'release_package'

    middleware = KingfisherTransformResizePackageMiddleware()

    package = {'releases': []}
    for i in range(200):
        package['releases'].append({'key': 'value'})

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', json.dumps(package))

    response = response_fixture(body=io.getvalue(), meta={'file_name': 'test.zip'})
    generator = spider.parse(response)
    item = next(generator)

    generator = middleware.process_spider_output(response, [item], spider)
    transformed_items = list(generator)

    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        assert len(item) == 6
        assert item['file_name'] == 'test.json'
        assert item['url'] == 'http://example.com'
        assert item['number'] == i
        assert len(json.loads(item['data'])['releases']) == len_releases
        assert item['data_type'] == 'release_package'
        assert item['encoding'] == 'utf-8'


@pytest.mark.parametrize('sample', [None, 5])
def test_line_delimited_json_middleware(sample):
    spider = spider_with_crawler(spider_class=SimpleSpider, sample=sample)
    spider.data_type = 'release_package'
    spider.line_delimited = True

    middleware = KingfisherTransformLineDelimitedJSONMiddleware()

    content = []
    for i in range(1, 21):
        content.append('{"key": %s}\n' % i)

    response = response_fixture(body=''.join(content), meta={'file_name': 'test.json'})
    generator = spider.parse(response)
    item = next(generator)

    generator = middleware.process_spider_output(response, [item], spider)
    transformed_items = list(generator)

    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        assert item == {
            'file_name': 'test.json',
            'url': 'http://example.com',
            'number': i,
            'data': '{"key": %s}\n' % i,
            'data_type': 'release_package',
            'encoding': 'utf-8'
        }


@pytest.mark.parametrize('sample', [None, 5])
def test_line_delimited_json_middleware_compressed(sample):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = 'release_package'
    spider.line_delimited = True

    middleware = KingfisherTransformLineDelimitedJSONMiddleware()

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
            'file_name': 'test.json',
            'url': 'http://example.com',
            'number': i,
            'data': '{"key": %s}\n' % i,
            'data_type': 'release_package',
            'encoding': 'utf-8'
        }
