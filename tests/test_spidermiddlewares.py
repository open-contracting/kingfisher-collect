import json
from io import BytesIO
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

import pytest

from kingfisher_scrapy.base_spiders import CompressedFileSpider, SimpleSpider
from kingfisher_scrapy.exceptions import RetryableError
from kingfisher_scrapy.items import File, FileError, FileItem
from kingfisher_scrapy.spidermiddlewares import (
    AddPackageMiddleware,
    CheckJSONFormatMiddleware,
    ConcatenatedJSONMiddleware,
    LineDelimitedMiddleware,
    ReadDataMiddleware,
    ResizePackageMiddleware,
    RetryDataErrorMiddleware,
    RootPathMiddleware,
)
from tests import response_fixture, spider_with_crawler


# https://discuss.python.org/t/enhance-builtin-iterables-like-list-range-with-async-methods-like-aiter-anext/21352/11
async def _aiter(iterable):
    for i in iterable:
        yield i


# https://stackoverflow.com/a/62585232/244258
async def alist(iterable):
    return [i async for i in iterable]


@pytest.mark.parametrize('middleware_class', [
    ConcatenatedJSONMiddleware,
    LineDelimitedMiddleware,
    CheckJSONFormatMiddleware,
    RootPathMiddleware,
    AddPackageMiddleware,
    ResizePackageMiddleware,
    ReadDataMiddleware,
])
@pytest.mark.parametrize('item', [
    File(
        file_name='test.json',
        url='http://test.com',
        data_type='release_package',
        data={},
    ),
    FileItem(
        file_name='test.json',
        url='http://test.com',
        data_type='release_package',
        data={},
        number=1,
    ),
    FileError(
        file_name='test.json',
        url='http://test.com',
        errors={},
    ),
])
async def test_passthrough(middleware_class, item):
    spider = spider_with_crawler()

    middleware = middleware_class()

    generator = middleware.process_spider_output(None, _aiter([item]), spider)
    returned_item = await anext(generator)

    assert item == returned_item


@pytest.mark.parametrize('middleware_class,attribute,value,override', [
    (ConcatenatedJSONMiddleware, 'concatenated_json', True,
     {'data': {'a': [{'b': 'c'}]}, 'number': 1}),
    (LineDelimitedMiddleware, 'line_delimited', True,
     {'data': b'{"a":[{"b": "c"}]}', 'number': 1}),
    (RootPathMiddleware, 'root_path', 'a.item',
     {'data':  {'releases': [{'b': 'c'}], 'version': '1.1'}, 'data_type': 'release_package', 'number': 1}),
    (AddPackageMiddleware, 'data_type', 'release',
     {'data': {'releases': [{'a': [{'b': 'c'}]}], 'version': '1.1'}, 'data_type': 'release_package'}),
    # ResizePackageMiddleware is only used with CompressedFileSpider and BigFileSpider.
    # ReadDataMiddleware is only used with file-like objects.
])
async def test_bytes_or_file(middleware_class, attribute, value, override, tmpdir):
    spider = spider_with_crawler()
    setattr(spider, attribute, value)

    middleware = middleware_class()

    data = b'{"a":[{"b": "c"}]}'
    bytes_item = File(
        file_name='test.json',
        url='http://test.com',
        data_type='release',
        data=data,
    )

    path = tmpdir.join('test.json')
    path.write(data, 'wb')
    with path.open('rb') as f:
        file_item = File(
            file_name='test.json',
            url='http://test.com',
            data_type='release',
            data=f,
        )

        generator = middleware.process_spider_output(None, _aiter([bytes_item, file_item]), spider)
        transformed_items = await alist(generator)

    expected = {
        'file_name': 'test.json',
        'url': 'http://test.com',
        'data_type': 'release',
        'path': '',
        'invalid_format': False,
    }
    expected.update(override)

    assert len(transformed_items) == 2
    for item in transformed_items:
        assert item.__dict__ == expected


@pytest.mark.parametrize('middleware_class,attribute,value,override', [
    (ConcatenatedJSONMiddleware, 'concatenated_json', True,
     {'data': {'name': 'ALCALDÍA MUNICIPIO DE TIBÚ'}, 'number': 1}),
    (RootPathMiddleware, 'root_path', 'name', {'data': 'ALCALDÍA MUNICIPIO DE TIBÚ'}),
])
async def test_encoding(middleware_class, attribute, value, override, tmpdir):
    spider = spider_with_crawler()
    setattr(spider, attribute, value)
    spider.encoding = 'iso-8859-1'

    middleware = middleware_class()

    data = b'{"name": "ALCALD\xcdA MUNICIPIO DE TIB\xda"}'
    bytes_item = File(
        file_name='test.json',
        url='http://test.com',
        data_type='release',
        data=data,
    )

    path = tmpdir.join('test.json')
    path.write(data, 'wb')
    with path.open('rb') as f:
        file_item = File(
            file_name='test.json',
            url='http://test.com',
            data_type='release',
            data=f,
        )

        generator = middleware.process_spider_output(None, _aiter([bytes_item, file_item]), spider)
        transformed_items = await alist(generator)

    expected = {
        'file_name': 'test.json',
        'url': 'http://test.com',
        'data_type': 'release',
        'path': '',
        'invalid_format': False,
    }
    expected.update(override)

    assert len(transformed_items) == 2
    for item in transformed_items:
        assert item.__dict__ == expected


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
async def test_add_package_middleware(data_type, data, root_path):
    spider = spider_with_crawler()
    spider.root_path = root_path

    root_path_middleware = RootPathMiddleware()
    add_package_middleware = AddPackageMiddleware()

    item = File(
        file_name='test.json',
        url='http://test.com',
        data_type=data_type,
        data=data,
    )

    generator = root_path_middleware.process_spider_output(None, _aiter([item]), spider)
    item = await anext(generator)
    generator = add_package_middleware.process_spider_output(None, _aiter([item]), spider)
    item = await anext(generator)

    expected = {
        'file_name': 'test.json',
        'url': 'http://test.com',
        'path': '',
        'invalid_format': False,
    }
    if 'item' in root_path:
        expected['number'] = 1

    if 'package' in data_type:
        expected['data'] = {f"{data_type[:-8]}s": [{"ocid": "abc"}], "uri": "test"}
        expected['data_type'] = data_type
    else:
        expected['data'] = {f"{data_type}s": [{"ocid": "abc"}], "version": spider.ocds_version}
        expected['data_type'] = f'{data_type}_package'

    assert item.__dict__ == expected


@pytest.mark.parametrize('sample,len_items,len_releases', [(None, 2, 100), (5, 5, 5), (200, 2, 100)])
@pytest.mark.parametrize('encoding,character', [('utf-8', b'\xc3\x9a'), ('iso-8859-1', b'\xda')])
@pytest.mark.parametrize('data_type, key', [('record_package', 'records'), ('release_package', 'releases')])
async def test_resize_package_middleware(sample, len_items, len_releases, encoding, character, data_type, key):
    spider = spider_with_crawler(spider_class=CompressedFileSpider, sample=sample)
    spider.data_type = data_type
    spider.resize_package = True
    spider.encoding = encoding

    middleware = ResizePackageMiddleware()

    package = {'publisher': {'name': 'TIBÚ'}, key: []}
    for i in range(200):
        package[key].append({'key': 'TIBÚ'})

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        data = json.dumps(package, ensure_ascii=False).encode()
        zipfile.writestr('test.json', data.replace(b'\xc3\x9a', character))

    response = response_fixture(body=io.getvalue(), meta={'file_name': 'archive.zip'})
    generator = spider.parse(response)
    item = next(generator)

    generator = middleware.process_spider_output(response, _aiter([item]), spider)
    transformed_items = await alist(generator)

    assert len(transformed_items) == len_items
    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        assert len(item.__dict__) == 7
        assert item.file_name == 'archive-test.json'
        assert item.url == 'http://example.com'
        assert item.number == i
        assert len(item.data[key]) == len_releases
        assert item.data_type == data_type


@pytest.mark.parametrize('middleware_class,attribute,separator', [
    (ConcatenatedJSONMiddleware, 'concatenated_json', ''),
    (LineDelimitedMiddleware, 'line_delimited', '\n'),
])
@pytest.mark.parametrize('sample', [None, 5])
async def test_json_streaming_middleware(middleware_class, attribute, separator, sample):
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

    generator = middleware.process_spider_output(response, _aiter([item]), spider)
    transformed_items = await alist(generator)

    length = sample if sample else 20

    assert len(transformed_items) == length
    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        if attribute == 'concatenated_json':
            data = {'key': i}
        else:
            data = ('{"key": %s}\n' % i).encode()
        assert item.__dict__ == {
            'file_name': 'test.json',
            'url': 'http://example.com',
            'data_type': 'release_package',
            'data': data,
            'number': i,
            'path': '',
            'invalid_format': False,
        }


@pytest.mark.parametrize('middleware_class,attribute,value', [
    (ConcatenatedJSONMiddleware, 'concatenated_json', True),
    (LineDelimitedMiddleware, 'line_delimited', True),
])
async def test_json_streaming_middleware_with_root_path_middleware(middleware_class, attribute, value):
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
    generator = stream_middleware.process_spider_output(response, _aiter([item]), spider)
    item = await anext(generator)

    generator = root_path_middleware.process_spider_output(response, _aiter([item]), spider)
    transformed_items = await alist(generator)

    assert len(transformed_items) == 1
    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        assert len(item.__dict__) == 7
        assert item.file_name == 'test.json'
        assert item.url == 'http://example.com'
        assert item.number == i
        assert item.data == {'releases': [{'key': i}]}
        assert item.data_type == 'release_package'


@pytest.mark.parametrize('middleware_class,attribute,value', [
    (ConcatenatedJSONMiddleware, 'concatenated_json', True),
    (LineDelimitedMiddleware, 'line_delimited', True),
])
@pytest.mark.parametrize('sample', [None, 5])
async def test_json_streaming_middleware_with_compressed_file_spider(middleware_class, attribute, value, sample):
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

    generator = stream_middleware.process_spider_output(response, _aiter([item]), spider)
    transformed_items = await alist(generator)

    length = sample if sample else 20

    assert len(transformed_items) == length
    for i, item in enumerate(transformed_items, 1):
        assert type(item) is FileItem
        if attribute == 'concatenated_json':
            data = {'key': i}
        else:
            data = ('{"key": %s}\n' % i).encode()
        assert item.__dict__ == {
            'file_name': 'archive-test.json',
            'url': 'http://example.com',
            'data_type': 'release_package',
            'data': data,
            'number': i,
            'path': '',
            'invalid_format': False,
        }


async def test_read_data_middleware():
    spider = spider_with_crawler(spider_class=CompressedFileSpider)
    spider.data_type = 'release_package'

    middleware = ReadDataMiddleware()

    io = BytesIO()
    with ZipFile(io, 'w', compression=ZIP_DEFLATED) as zipfile:
        zipfile.writestr('test.json', '{}')

    response = response_fixture(body=io.getvalue(), meta={'file_name': 'archive.zip'})
    generator = spider.parse(response)
    item = next(generator)

    generator = middleware.process_spider_output(response, _aiter([item]), spider)
    transformed_items = await alist(generator)

    assert len(transformed_items) == 1
    assert transformed_items[0].data == b'{}'


@pytest.mark.parametrize('exception', [BadZipFile(), RetryableError, Exception()])
def test_retry_data_error_middleware(exception):
    spider = spider_with_crawler()
    response = response_fixture()
    middleware = RetryDataErrorMiddleware()

    generator = middleware.process_spider_exception(response, exception, spider)

    if isinstance(exception, (BadZipFile, RetryableError)):
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


@pytest.mark.parametrize('root_path,data_type,data,expected_data_type,expected_data', [
    # Empty root path.
    ('',
     'release', {'a': 'b'},
     'release', {'a': 'b'}),
    # Root path without "item".
    ('x',
     'release', {'x': {'a': 'b'}},
     'release', {'a': 'b'}),
    # Root paths with "item" ...
    # ... with an empty array, for data_type = "release".
    ('item',
     'release', [],
     'release_package', {'releases': [], 'version': '1.1'}),
    # ... with an empty array, for data_type = "record_package".
    ('item',
     'record_package', [],
     'record_package', {'records': [], 'version': '1.1'}),
])
@pytest.mark.parametrize('klass', [File, FileItem])
async def test_root_path_middleware(root_path, data_type, data, expected_data_type, expected_data, klass):
    spider = spider_with_crawler()
    middleware = RootPathMiddleware()
    spider.data_type = data_type
    spider.root_path = root_path

    kwargs = {'number': 1} if klass is FileItem else {}

    item = klass(
        file_name='test.json',
        url='http://test.com',
        data_type=data_type,
        data=data,
        **kwargs
    )

    generator = middleware.process_spider_output(None, _aiter([item]), spider)
    transformed_items = await alist(generator)

    assert len(transformed_items) == 1
    for transformed_item in transformed_items:
        assert isinstance(transformed_item, klass)
        assert transformed_item.file_name == 'test.json'
        assert transformed_item.data == expected_data
        assert transformed_item.data_type == expected_data_type
        assert transformed_item.url == 'http://test.com'


@pytest.mark.parametrize('root_path,sample,data_type,data,expected_data_type,expected_data', [
    # ... for data_type = "release".
    ('item', None,
     'release', [{'a': 'b'}, {'c': 'd'}],
     'release_package', {'releases': [{'a': 'b'}, {'c': 'd'}], 'version': '1.1'}),
    # ... and another prefix, for data_type = "record".
    ('x.item', None,
     'record', {'x': [{'a': 'b'}, {'c': 'd'}]},
     'record_package', {'records': [{'a': 'b'}, {'c': 'd'}], 'version': '1.1'}),
    # ... and "sample".
    ('x.item', 1,
     'record', {'x': [{'a': 'b'}, {'c': 'd'}]},
     'record_package', {'records': [{'a': 'b'}], 'version': '1.1'}),
    # ... without package metadata, for data_type = "record_package".
    ('item', None,
     'record_package', [{'records': [{'a': 'b'}, {'c': 'd'}]}, {'records': [{'e': 'f'}, {'g': 'h'}]}],
     'record_package', {'records': [{'a': 'b'}, {'c': 'd'}, {'e': 'f'}, {'g': 'h'}]}),
    # ... with inconsistent package metadata, for data_type = "release_package".
    ('item', None,
     'release_package', [{'releases': [{'a': 'b'}, {'c': 'd'}], 'x': 'y'}, {'releases': [{'e': 'f'}, {'g': 'h'}]}],
     'release_package', {'releases': [{'a': 'b'}, {'c': 'd'}, {'e': 'f'}, {'g': 'h'}], 'x': 'y'}),
])
@pytest.mark.parametrize('klass', [File, FileItem])
async def test_root_path_middleware_item(root_path, sample, data_type, data, expected_data_type, expected_data, klass):
    spider = spider_with_crawler()
    middleware = RootPathMiddleware()
    spider.data_type = data_type
    spider.root_path = root_path
    spider.sample = sample

    kwargs = {'number': 1} if klass is FileItem else {}

    item = klass(
        file_name='test.json',
        url='http://test.com',
        data_type=data_type,
        data=data,
        **kwargs
    )

    generator = middleware.process_spider_output(None, _aiter([item]), spider)
    transformed_items = await alist(generator)

    assert len(transformed_items) == 1
    for transformed_item in transformed_items:
        assert isinstance(transformed_item, FileItem)
        assert transformed_item.number == 1
        assert transformed_item.file_name == 'test.json'
        assert transformed_item.data == expected_data
        assert transformed_item.data_type == expected_data_type
        assert transformed_item.url == 'http://test.com'


@pytest.mark.parametrize('invalid', [True, False])
@pytest.mark.parametrize('klass', [File, FileItem])
async def test_check_json_format_middleware(invalid, klass):
    spider = spider_with_crawler()
    middleware = CheckJSONFormatMiddleware()
    spider.check_json_format = True

    kwargs = {'number': 1} if klass is FileItem else {}

    item = klass(
        file_name='test.json',
        url='http://test.com',
        data_type='release_package',
        data='{"key": "value"}',
        **kwargs
    )

    if invalid:
        item.data = '{"broken": }'

    generator = middleware.process_spider_output(None, _aiter([item]), spider)
    transformed_items = await alist(generator)

    assert len(transformed_items) == 1
    for transformed_item in transformed_items:
        assert transformed_item.invalid_format is invalid
