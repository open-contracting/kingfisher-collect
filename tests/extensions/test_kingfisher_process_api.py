import json
import os
from unittest.mock import PropertyMock, patch

import pytest
import pytest_twisted
from scrapy.exceptions import NotConfigured
from scrapy.http import Request, Response
from twisted.python.failure import Failure

from kingfisher_scrapy.extensions import FilesStore, KingfisherProcessAPI
from kingfisher_scrapy.items import FileError, FileItem, PluckedItem
from tests import spider_with_crawler, spider_with_files_store


class ExpectedError(Exception):
    pass


def test_from_crawler():
    spider = spider_with_crawler(settings={
        'KINGFISHER_API_URI': 'http://httpbin.org/anything',
        'KINGFISHER_API_KEY': 'xxx',
        'KINGFISHER_API_LOCAL_DIRECTORY': 'localdir',
    })

    extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    assert extension.directory == 'localdir'


@pytest.mark.parametrize('api_url,api_key', [
    (None, None),
    ('http://httpbin.org/anything', None),
    (None, 'xxx'),
])
def test_from_crawler_missing_arguments(api_url, api_key):
    spider = spider_with_crawler(settings={
        'KINGFISHER_API_URI': api_url,
        'KINGFISHER_API_KEY': api_key,
    })

    with pytest.raises(NotConfigured) as excinfo:
        KingfisherProcessAPI.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'KINGFISHER_API_URI and/or KINGFISHER_API_KEY is not set.'


def test_from_crawler_with_database_url():
    spider = spider_with_crawler(crawl_time='2021-05-25T00:00:00', settings={
        'KINGFISHER_API_URI': 'test',
        'KINGFISHER_API_KEY': 'test',
        'DATABASE_URL': 'test',
    })

    with pytest.raises(NotConfigured) as excinfo:
        KingfisherProcessAPI.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'DATABASE_URL is set.'


@pytest_twisted.inlineCallbacks
@pytest.mark.parametrize('sample,is_sample,path', [
    (None, False, os.path.join('test', '20010203_040506', 'file.json')),
    ('true', True, os.path.join('test_sample', '20010203_040506', 'file.json')),
])
@pytest.mark.parametrize('note', ['', 'Started by NAME.'])
@pytest.mark.parametrize('encoding,encoding2', [(None, 'utf-8'), ('iso-8859-1', 'iso-8859-1')])
@pytest.mark.parametrize('ok', [True, False])
@pytest.mark.parametrize('directory', [True, False])
@pytest.mark.parametrize('crawl_time', [None, '2020-01-01T00:00:00'])
def test_item_scraped_file(sample, is_sample, path, note, encoding, encoding2, directory, ok, crawl_time, tmpdir,
                           caplog):
    with patch('treq.response._Response.code', new_callable=PropertyMock) as mocked:
        mocked.return_value = 200 if ok else 400

        settings = {}
        if directory:
            settings['KINGFISHER_API_LOCAL_DIRECTORY'] = str(tmpdir.join('xxx'))
        spider = spider_with_files_store(tmpdir, settings=settings, sample=sample, note=note, crawl_time=crawl_time)
        extension = KingfisherProcessAPI.from_crawler(spider.crawler)

        kwargs = {}
        if encoding:
            kwargs['encoding'] = encoding
        item = spider.build_file(
            file_name='file.json',
            url='https://example.com/remote.json',
            data=b'{"key": "value"}',
            data_type='release_package',
            **kwargs,
        )

        store_extension = FilesStore.from_crawler(spider.crawler)
        store_extension.item_scraped(item, spider)

        response = yield extension.item_scraped(item, spider)

        data = yield response.json()

        form = {
            'collection_source': 'test',
            'collection_data_version': '2001-02-03 04:05:06',
            'collection_sample': str(is_sample),
            'collection_ocds_version': '1.1',
            'file_name': 'file.json',
            'url': 'https://example.com/remote.json',
            # Specific to File.
            'data_type': 'release_package',
            'encoding': encoding2,
        }
        if note:
            form['collection_note'] = note
        if crawl_time:
            form['collection_data_version'] = '2020-01-01 00:00:00'
            path = path.replace('20010203_040506', '20200101_000000')
        if directory:
            form['local_file_name'] = tmpdir.join('xxx', path)

        with open(tmpdir.join(path)) as f:
            assert data['method'] == 'POST'
            assert data['url'] == 'http://httpbin.org/anything/api/v1/submit/file/'
            assert data['headers']['Authorization'] == 'ApiKey xxx'
            assert data['form'] == form
            assert data['args'] == {}
            assert data['data'] == ''
            if directory:
                assert data['files'] == {}
            else:
                assert data['files'] == {'file': f.read()}

        if not ok:
            message = 'create_file failed (https://example.com/remote.json) with status code: 400'

            assert len(caplog.records) == 1
            assert caplog.records[0].name == 'test'
            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].message == message


@pytest_twisted.inlineCallbacks
@pytest.mark.parametrize('sample,is_sample', [(None, False), ('true', True)])
@pytest.mark.parametrize('note', [None, 'Started by NAME.'])
@pytest.mark.parametrize('encoding', ['utf-8', 'iso-8859-1'])
@pytest.mark.parametrize('ok', [True, False])
def test_item_scraped_file_item(sample, is_sample, note, encoding, ok, tmpdir, caplog):
    with patch('treq.response._Response.code', new_callable=PropertyMock) as mocked:
        mocked.return_value = 200 if ok else 400

        spider = spider_with_files_store(tmpdir, sample=sample, note=note)
        extension = KingfisherProcessAPI.from_crawler(spider.crawler)

        item = FileItem({
            'number': 1,
            'file_name': 'data.json',
            'data': b'{"key": "value"}',
            'data_type': 'release_package',
            'url': 'https://example.com/remote.json',
            'encoding': encoding,
        })

        response = yield extension.item_scraped(item, spider)
        data = yield response.json()

        form = {
            'collection_source': 'test',
            'collection_data_version': '2001-02-03 04:05:06',
            'collection_sample': str(is_sample),
            'collection_ocds_version': '1.1',
            'file_name': 'data.json',
            'url': 'https://example.com/remote.json',
            # Specific to FileItem.
            'data_type': 'release_package',
            'encoding': encoding,
            'number': '1',
            'data': '{"key": "value"}',
        }
        if note:
            form['collection_note'] = note

        assert data['method'] == 'POST'
        assert data['url'] == 'http://httpbin.org/anything/api/v1/submit/item/'
        assert data['headers']['Authorization'] == 'ApiKey xxx'
        assert data['form'] == form
        assert data['args'] == {}
        assert data['data'] == ''
        assert data['files'] == {}

        if not ok:
            message = 'create_file_item failed (https://example.com/remote.json) with status code: 400'

            assert len(caplog.records) == 1
            assert caplog.records[0].name == 'test'
            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].message == message


def test_item_scraped_plucked_item(tmpdir):
    spider = spider_with_files_store(tmpdir)
    extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    item = PluckedItem({
        'value': '123',
    })

    response = extension.item_scraped(item, spider)

    assert response is None


@pytest_twisted.inlineCallbacks
@pytest.mark.parametrize('sample,is_sample', [(None, False), ('true', True)])
@pytest.mark.parametrize('ok', [True, False])
def test_item_scraped_file_error(sample, is_sample, ok, tmpdir, caplog):
    with patch('treq.response._Response.code', new_callable=PropertyMock) as mocked:
        mocked.return_value = 200 if ok else 400

        spider = spider_with_files_store(tmpdir, sample=sample)
        extension = KingfisherProcessAPI.from_crawler(spider.crawler)

        item = FileError({
            'file_name': 'file.json',
            'url': 'https://example.com/remote.json',
            'errors': {'http_code': 500},
        })

        response = yield extension.item_scraped(item, spider)
        data = yield response.json()

        form = {
            'collection_source': 'test',
            'collection_data_version': '2001-02-03 04:05:06',
            'collection_sample': str(is_sample),
            'collection_ocds_version': '1.1',
            'file_name': 'file.json',
            'url': 'https://example.com/remote.json',
            # Specific to FileError.
            'errors': '{"http_code": 500}',
        }

        assert data['method'] == 'POST'
        assert data['url'] == 'http://httpbin.org/anything/api/v1/submit/file_errors/'
        assert data['headers']['Authorization'] == 'ApiKey xxx'
        assert data['form'] == form
        assert data['args'] == {}
        assert data['data'] == ''
        assert data['files'] == {}

        if not ok:
            message = 'create_file_error failed (https://example.com/remote.json) with status code: 400'

            assert len(caplog.records) == 1
            assert caplog.records[0].name == 'test'
            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].message == message


@pytest_twisted.inlineCallbacks
@pytest.mark.parametrize('sample,is_sample', [(None, False), ('true', True)])
@pytest.mark.parametrize('ok', [True, False])
def test_item_error(sample, is_sample, ok, tmpdir, caplog):
    try:
        {}['nonexistent']
    except KeyError:
        failure = Failure()

    with patch('treq.response._Response.code', new_callable=PropertyMock) as mocked:
        mocked.return_value = 200 if ok else 400

        spider = spider_with_files_store(tmpdir, sample=sample)
        extension = KingfisherProcessAPI.from_crawler(spider.crawler)

        item = FileError({
            'file_name': 'file.json',
            'url': 'https://example.com/remote.json',
        })

        scrapy_request = yield Request('https://example.com/remote.json')
        scrapy_response = Response('https://example.com/remote.json', request=scrapy_request)
        response = yield extension.item_error(item, scrapy_response, spider, failure)
        data = yield response.json()
        errors = json.loads(data['form'].pop('errors'))

        form = {
            'collection_source': 'test',
            'collection_data_version': '2001-02-03 04:05:06',
            'collection_sample': str(is_sample),
            'collection_ocds_version': '1.1',
            'file_name': 'file.json',
            'url': 'https://example.com/remote.json',
        }

        assert data['method'] == 'POST'
        assert data['url'] == 'http://httpbin.org/anything/api/v1/submit/file_errors/'
        assert data['headers']['Authorization'] == 'ApiKey xxx'
        assert data['form'] == form
        assert data['args'] == {}
        assert data['data'] == ''
        assert data['files'] == {}

        assert len(errors) == 1
        assert errors['twisted'].startswith("[Failure instance: Traceback: <class 'KeyError'>: 'nonexistent'\n")

        if not ok:
            message = 'create_file_error failed (file.json) with status code: 400'

            assert len(caplog.records) == 1
            assert caplog.records[0].name == 'test'
            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].message == message


@pytest_twisted.inlineCallbacks
@pytest.mark.parametrize('sample,is_sample', [(None, False), ('true', True)])
@pytest.mark.parametrize('ok', [True, False])
def test_spider_closed(sample, is_sample, ok, tmpdir, caplog):
    with patch('treq.response._Response.code', new_callable=PropertyMock) as mocked:
        mocked.return_value = 200 if ok else 400

        spider = spider_with_files_store(tmpdir, sample=sample)
        extension = KingfisherProcessAPI.from_crawler(spider.crawler)

        response = yield extension.spider_closed(spider, 'sample' if is_sample else 'finished')
        data = yield response.json()

        form = {
            'collection_source': 'test',
            'collection_data_version': '2001-02-03 04:05:06',
            'collection_sample': str(is_sample),
            'collection_ocds_version': '1.1',
        }

        assert data['method'] == 'POST'
        assert data['url'] == 'http://httpbin.org/anything/api/v1/submit/end_collection_store/'
        assert data['headers']['Authorization'] == 'ApiKey xxx'
        assert data['form'] == form
        assert data['args'] == {}
        assert data['data'] == ''
        assert data['files'] == {}

        if not ok:
            message = 'end_collection_store failed (test) with status code: 400'

            assert len(caplog.records) == 1
            assert caplog.records[0].name == 'test'
            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].message == message


@pytest.mark.parametrize('attribute', ['pluck', 'keep_collection_open'])
@pytest_twisted.inlineCallbacks
def test_spider_closed_return(attribute, tmpdir):
    spider = spider_with_files_store(tmpdir)
    setattr(spider, attribute, True)

    extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    response = extension.spider_closed(spider, 'xxx')

    assert response is None


@pytest_twisted.inlineCallbacks
def test_spider_closed_exception(tmpdir, caplog):
    with patch('treq.response._Response.code', new_callable=PropertyMock) as mocked:
        mocked.side_effect = ExpectedError

        spider = spider_with_files_store(tmpdir)
        extension = KingfisherProcessAPI.from_crawler(spider.crawler)

        with pytest.raises(ExpectedError):
            yield extension.spider_closed(spider, 'finished')


@pytest_twisted.inlineCallbacks
def test_spider_closed_other_reason(tmpdir):
    spider = spider_with_files_store(tmpdir)
    extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    response = extension.spider_closed(spider, 'xxx')

    assert response is None


@pytest_twisted.inlineCallbacks
@pytest.mark.parametrize('sample,is_sample', [(None, False), ('true', True)])
@pytest.mark.parametrize('ok', [True, False])
def test_spider_error(sample, is_sample, ok, tmpdir, caplog):
    try:
        {}['nonexistent']
    except KeyError:
        failure = Failure()

    with patch('treq.response._Response.code', new_callable=PropertyMock) as mocked:
        mocked.return_value = 200 if ok else 400

        spider = spider_with_files_store(tmpdir, sample=sample)
        extension = KingfisherProcessAPI.from_crawler(spider.crawler)

        scrapy_request = yield Request('https://example.com/remote.json')
        scrapy_response = Response('https://example.com/remote.json', request=scrapy_request)
        response = yield extension.spider_error(failure, scrapy_response, spider)
        data = yield response.json()
        errors = json.loads(data['form'].pop('errors'))

        form = {
            'collection_source': 'test',
            'collection_data_version': '2001-02-03 04:05:06',
            'collection_sample': str(is_sample),
            'collection_ocds_version': '1.1',
            'file_name': 'https://example.com/remote.json',
            'url': 'https://example.com/remote.json',
        }

        assert data['method'] == 'POST'
        assert data['url'] == 'http://httpbin.org/anything/api/v1/submit/file_errors/'
        assert data['headers']['Authorization'] == 'ApiKey xxx'
        assert data['form'] == form
        assert data['args'] == {}
        assert data['data'] == ''
        assert data['files'] == {}

        assert len(errors) == 1
        assert errors['twisted'].startswith("[Failure instance: Traceback: <class 'KeyError'>: 'nonexistent'\n")

        if not ok:
            message = 'create_file_error failed (https://example.com/remote.json) with status code: 400'

            assert len(caplog.records) == 1
            assert caplog.records[0].name == 'test'
            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].message == message
