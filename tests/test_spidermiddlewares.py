import json
from io import BytesIO
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

import pytest

from kingfisher_scrapy.base_spiders import CompressedFileSpider, SimpleSpider
from kingfisher_scrapy.items import File, FileError, FileItem
from kingfisher_scrapy.spidermiddlewares import (AddPackageMiddleware, ConcatenatedJSONMiddleware,
                                                 LineDelimitedMiddleware, ReadDataMiddleware, ResizePackageMiddleware,
                                                 RetryDataErrorMiddleware, RootPathMiddleware)
from tests import response_fixture, spider_with_crawler


@pytest.mark.parametrize('middleware_class', [
    ConcatenatedJSONMiddleware,
    LineDelimitedMiddleware,
    RootPathMiddleware,
    AddPackageMiddleware,
    ResizePackageMiddleware,
    ReadDataMiddleware,
])
@pytest.mark.parametrize('item', [
    File({
        'file_name': 'test.json',
        'data': 'data',
        'data_type': 'release_package',
        'url': 'http://test.com',
    }),
    FileItem({
        'file_name': 'test.json',
        'data': 'data',
        'data_type': 'release_package',
        'url': 'http://test.com',
        'number': 1,
    }),
    FileError({
        'file_name': 'test.json',
        'url': 'http://test.com',
        'errors': '',
    }),
])
def test_passthrough(middleware_class, item):
    spider = spider_with_crawler()

    middleware = middleware_class()

    generator = middleware.process_spider_output(None, [item], spider)
    returned_item = next(generator)

    assert item == returned_item


@pytest.mark.parametrize('middleware_class,attribute,value,override', [
    (ConcatenatedJSONMiddleware, 'concatenated_json', True, {'data': {'a': [{'b': 'c'}]}, 'number': 1}),
    (LineDelimitedMiddleware, 'line_delimited', True, {'data': b'{"a":[{"b": "c"}]}', 'number': 1}),
    (RootPathMiddleware, 'root_path', 'a.item',
     {'data':  {'releases': [{'b': 'c'}], 'version': '1.1'}, 'data_type': 'release_package'}),
    (AddPackageMiddleware, 'data_type', 'release',
     {'data': {'releases': [{'a': [{'b': 'c'}]}], 'version': '1.1'}, 'data_type': 'release_package'}),
    # ResizePackageMiddleware is only used with CompressedFileSpider and BigFileSpider.
    # ReadDataMiddleware is only used with file-like objects.
])
def test_bytes_or_file(middleware_class, attribute, value, override, tmpdir):
    spider = spider_with_crawler()
    setattr(spider, attribute, value)

    middleware = middleware_class()

    data = b'{"a":[{"b": "c"}]}'
    bytes_item = File({
        'file_name': 'test.json',
        'data': data,
        'data_type': 'release',
        'url': 'http://test.com',
    })

    path = tmpdir.join('test.json')
    path.write(data, 'wb')
    file_item = File({
        'file_name': 'test.json',
        'data': path.open('rb'),
        'data_type': 'release',
        'url': 'http://test.com',
    })

    generator = middleware.process_spider_output(None, [bytes_item, file_item], spider)
    transformed_items = list(generator)

    assert len(transformed_items) == 2
    for item in transformed_items:
        expected = {
            'file_name': 'test.json',
            'data_type': 'release',
            'url': 'http://test.com',
        }
        expected.update(override)
        assert item == expected


@pytest.mark.parametrize('middleware_class,attribute,value,override', [
    (ConcatenatedJSONMiddleware, 'concatenated_json', True,
     {'data': {'name': 'ALCALDÍA MUNICIPIO DE TIBÚ'}, 'number': 1}),
    (RootPathMiddleware, 'root_path', 'name', {'data': 'ALCALDÍA MUNICIPIO DE TIBÚ'}),
])
def test_encoding(middleware_class, attribute, value, override, tmpdir):
    spider = spider_with_crawler()
    setattr(spider, attribute, value)
    spider.encoding = 'iso-8859-1'

    middleware = middleware_class()

    data = b'{"name": "ALCALD\xcdA MUNICIPIO DE TIB\xda"}'
    bytes_item = File({
        'file_name': 'test.json',
        'data': data,
        'data_type': 'release',
        'url': 'http://test.com',
    })

    path = tmpdir.join('test.json')
    path.write(data, 'wb')
    file_item = File({
        'file_name': 'test.json',
        'data': path.open('rb'),
        'data_type': 'release',
        'url': 'http://test.com',
    })

    generator = middleware.process_spider_output(None, [bytes_item, file_item], spider)
    transformed_items = list(generator)

    assert len(transformed_items) == 2
    expected = {
            'file_name': 'test.json',
            'data_type': 'release',
            'url': 'http://test.com',
        }
    expected.update(override)
    for item in transformed_items:
        assert item == expected


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
def test_add_package_middleware(data_type, data, root_path):
    spider = spider_with_crawler()
    spider.root_path = root_path

    root_path_middleware = RootPathMiddleware()
    add_package_middleware = AddPackageMiddleware()

    item = File({
        'file_name': 'test.json',
        'data': data,
        'data_type': data_type,
        'url': 'http://test.com',
    })

    generator = root_path_middleware.process_spider_output(None, [item], spider)
    item = next(generator)
    generator = add_package_middleware.process_spider_output(None, [item], spider)
    item = next(generator)

    expected = {
        'file_name': 'test.json',
        'url': 'http://test.com',
    }

    if 'package' in data_type:
        expected['data'] = {f"{data_type[:-8]}s": [{"ocid": "abc"}], "uri": "test"}
        expected['data_type'] = data_type
    else:
        expected['data'] = {f"{data_type}s": [{"ocid": "abc"}], "version": spider.ocds_version}
        expected['data_type'] = f'{data_type}_package'

    assert item == expected


@pytest.mark.parametrize('sample,len_items,len_releases', [(None, 2, 100), (5, 5, 5)])
@pytest.mark.parametrize('encoding,character', [('utf-8', b'\xc3\x9a'), ('iso-8859-1', b'\xda')])
def test_resize_package_middleware(sample, len_items, len_releases, encoding, character):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = 'release_package'
    spider.resize_package = True
    spider.encoding = encoding

    middleware = ResizePackageMiddleware()

    package = {'publisher': {'name': 'TIBÚ'}, 'releases': []}
    for i in range(200):
        package['releases'].append({'key': 'TIBÚ'})

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        data = json.dumps(package, ensure_ascii=False).encode()
        zipfile.writestr('test.json', data.replace(b'\xc3\x9a', character))

    response = response_fixture(body=io.getvalue(), meta={'file_name': 'archive.zip'})
    generator = spider.parse(response)
    item = next(generator)

    generator = middleware.process_spider_output(response, [item], spider)
    transformed_items = list(generator)

    assert len(transformed_items) == len_items
    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        assert len(item) == 5
        assert item['file_name'] == 'archive-test.json'
        assert item['url'] == 'http://example.com'
        assert item['number'] == i
        assert isinstance(item['data'], bytes)
        assert len(json.loads(item['data'])['releases']) == len_releases
        assert item['data_type'] == 'release_package'


@pytest.mark.parametrize('middleware_class,attribute,separator', [
    (ConcatenatedJSONMiddleware, 'concatenated_json', ''),
    (LineDelimitedMiddleware, 'line_delimited', '\n'),
])
@pytest.mark.parametrize('sample', [None, 5])
def test_json_streaming_middleware(middleware_class, attribute, separator, sample):
    spider = spider_with_crawler(spider_class=SimpleSpider, sample=sample)
    spider.data_type = 'release_package'
    setattr(spider, attribute, True)

    middleware = middleware_class()

    content = []
    for i in range(1, 21):
        content.append('{"key": %s}%s' % (i, separator))

    response = response_fixture(body=''.join(content), meta={'file_name': 'test.json'})
    generator = spider.parse(response)
    item = next(generator)

    generator = middleware.process_spider_output(response, [item], spider)
    transformed_items = list(generator)

    length = sample if sample else 20

    assert len(transformed_items) == length
    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        if attribute == 'concatenated_json':
            data = {'key': i}
        else:
            data = ('{"key": %s}\n' % i).encode()
        assert item == {
            'file_name': 'test.json',
            'url': 'http://example.com',
            'number': i,
            'data': data,
            'data_type': 'release_package',
        }


@pytest.mark.parametrize('middleware_class,attribute,value', [
    (ConcatenatedJSONMiddleware, 'concatenated_json', True),
    (LineDelimitedMiddleware, 'line_delimited', True),
])
def test_json_streaming_middleware_with_root_path_middleware(middleware_class, attribute, value):
    spider = spider_with_crawler(spider_class=SimpleSpider)
    spider.data_type = 'release_package'
    setattr(spider, attribute, value)
    spider.root_path = 'results.item'

    stream_middleware = middleware_class()
    root_path_middleware = RootPathMiddleware()

    content = []
    for i in range(1, 21):
        content.append('{"results": [{"releases": [{"key": %s}]}]}\n' % i)

    response = response_fixture(body=''.join(content), meta={'file_name': 'test.json'})
    generator = spider.parse(response)
    item = next(generator)
    generator = stream_middleware.process_spider_output(response, [item], spider)
    item = next(generator)

    generator = root_path_middleware.process_spider_output(response, [item], spider)
    transformed_items = list(generator)

    assert len(transformed_items) == 1
    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        assert len(item) == 5
        assert item['file_name'] == 'test.json'
        assert item['url'] == 'http://example.com'
        assert item['number'] == i
        assert item['data'] == {'releases': [{'key': i}]}
        assert item['data_type'] == 'release_package'


@pytest.mark.parametrize('middleware_class,attribute,value', [
    (ConcatenatedJSONMiddleware, 'concatenated_json', True),
    (LineDelimitedMiddleware, 'line_delimited', True),
])
@pytest.mark.parametrize('sample', [None, 5])
def test_json_streaming_middleware_with_compressed_file_spider(middleware_class, attribute, value, sample):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = 'release_package'
    setattr(spider, attribute, value)

    stream_middleware = middleware_class()

    content = []
    for i in range(1, 21):
        content.append('{"key": %s}\n' % i)

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', ''.join(content))

    response = response_fixture(body=io.getvalue(), meta={'file_name': 'archive.zip'})
    generator = spider.parse(response)
    item = next(generator)

    generator = stream_middleware.process_spider_output(response, [item], spider)
    transformed_items = list(generator)

    length = sample if sample else 20

    assert len(transformed_items) == length
    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        if attribute == 'concatenated_json':
            data = {'key': i}
        else:
            data = ('{"key": %s}\n' % i).encode()
        assert item == {
            'file_name': 'archive-test.json',
            'url': 'http://example.com',
            'number': i,
            'data': data,
            'data_type': 'release_package',
        }


def test_read_data_middleware():
    spider = spider_with_crawler(spider_class=CompressedFileSpider)
    spider.data_type = 'release_package'

    middleware = ReadDataMiddleware()

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', '{}')

    response = response_fixture(body=io.getvalue(), meta={'file_name': 'archive.zip'})
    generator = spider.parse(response)
    item = next(generator)

    generator = middleware.process_spider_output(response, [item], spider)
    transformed_items = list(generator)

    assert len(transformed_items) == 1
    assert transformed_items[0]['data'] == b'{}'


@pytest.mark.parametrize('exception', [BadZipFile(), Exception()])
def test_retry_data_error_middleware(exception):
    spider = spider_with_crawler()
    response = response_fixture()
    middleware = RetryDataErrorMiddleware()

    generator = middleware.process_spider_exception(response, exception, spider)

    if isinstance(exception, BadZipFile):
        request = next(generator)

        assert request.dont_filter is True
        assert request.meta['retries'] == 1
        assert request.url == response.request.url

        response.request.meta['retries'] = 3
        generator = middleware.process_spider_exception(response, exception, spider)

        assert not list(generator)
    else:
        with pytest.raises(Exception):
            list(generator)
