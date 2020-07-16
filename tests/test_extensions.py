import json
import os
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import pytest
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.extensions import KingfisherFilesStore, KingfisherLatestDate, KingfisherProcessAPI
from kingfisher_scrapy.items import FileError, LatestReleaseDateItem
from tests import spider_with_crawler


def spider_with_files_store(files_store, **kwargs):
    spider = spider_with_crawler(**kwargs)
    spider.crawler.settings['FILES_STORE'] = files_store
    spider.crawler.settings['KINGFISHER_API_URI'] = 'http://httpbin.org/anything'
    spider.crawler.settings['KINGFISHER_API_KEY'] = 'xxx'

    return spider


def test_from_crawler():
    spider = spider_with_crawler()
    spider.crawler.settings['KINGFISHER_API_URI'] = 'http://httpbin.org/anything'
    spider.crawler.settings['KINGFISHER_API_KEY'] = 'xxx'
    spider.crawler.settings['KINGFISHER_API_LOCAL_DIRECTORY'] = 'localdir'

    api_extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    assert api_extension.directory == 'localdir'


@pytest.mark.parametrize('api_url,api_key', [
    (None, None),
    ('http://httpbin.org/anything', None),
    (None, 'xxx'),
])
def test_from_crawler_missing_arguments(api_url, api_key):
    spider = spider_with_crawler()
    spider.crawler.settings['KINGFISHER_API_URI'] = api_url
    spider.crawler.settings['KINGFISHER_API_KEY'] = api_key

    with pytest.raises(NotConfigured) as excinfo:
        KingfisherProcessAPI.from_crawler(spider.crawler)

    assert str(excinfo.value) == 'KINGFISHER_API_URI and/or KINGFISHER_API_KEY is not set.'


@pytest.mark.parametrize('sample,is_sample,path', [
    (None, False, os.path.join('test', '20010203_040506', 'file.json')),
    ('true', True, os.path.join('test_sample', '20010203_040506', 'file.json')),
])
@pytest.mark.parametrize('note', ['', 'Started by NAME.'])
@pytest.mark.parametrize('encoding,encoding2', [(None, 'utf-8'), ('iso-8859-1', 'iso-8859-1')])
@pytest.mark.parametrize('directory', [False, True])
@pytest.mark.parametrize('ok', [True, False])
@pytest.mark.parametrize('post_to_api', [True, False])
def test_item_scraped_file(sample, is_sample, path, note, encoding, encoding2, directory, ok, post_to_api, tmpdir,
                           caplog):
    spider = spider_with_files_store(tmpdir, sample=sample, note=note)

    if directory:
        spider.crawler.settings['KINGFISHER_API_LOCAL_DIRECTORY'] = str(tmpdir.join('xxx'))

    store_extension = KingfisherFilesStore.from_crawler(spider.crawler)
    api_extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    kwargs = {}
    if encoding:
        kwargs['encoding'] = encoding
    item = spider.build_file(file_name='file.json', url='https://example.com/remote.json', data=b'{"key": "value"}',
                             data_type='release_package', post_to_api=post_to_api, **kwargs)

    store_extension.item_scraped(item, spider)

    with patch('requests.post') as mocked:
        response = Mock()
        response.ok = ok
        response.status_code = 400
        mocked.return_value = response

        api_extension.item_scraped(item, spider)

        if not ok:
            if not post_to_api:
                assert len(caplog.records) == 0
            else:
                message = 'Failed to post [https://example.com/remote.json]. API status code: 400'

                assert len(caplog.records) == 1
                assert caplog.records[0].name == 'test'
                assert caplog.records[0].levelname == 'WARNING'
                assert caplog.records[0].message == message

        expected = {
            'collection_source': 'test',
            'collection_data_version': '2001-02-03 04:05:06',
            'collection_sample': is_sample,
            'file_name': 'file.json',
            'url': 'https://example.com/remote.json',
            # Specific to this test case.
            'data_type': 'release_package',
            'encoding': encoding2,
        }
        if note:
            expected['collection_note'] = note
        if directory:
            expected['local_file_name'] = tmpdir.join('xxx', path)
        if not post_to_api:
            assert mocked.call_count == 0
        else:
            with open(tmpdir.join(path), 'rb') as f:
                assert mocked.call_count == 1
                assert mocked.call_args[0] == ('http://httpbin.org/anything/api/v1/submit/file/',)
                assert mocked.call_args[1]['headers'] == {'Authorization': 'ApiKey xxx'}
                assert mocked.call_args[1]['data'] == expected
                assert mocked.call_args[1]['proxies'] == {'http': None, 'https': None}
                assert len(mocked.call_args[1]) == 4

                if directory:
                    assert mocked.call_args[1]['files'] == {}
                else:
                    assert len(mocked.call_args[1]['files']) == 1
                    assert len(mocked.call_args[1]['files']['file']) == 3
                    assert mocked.call_args[1]['files']['file'][0] == 'file.json'
                    assert mocked.call_args[1]['files']['file'][1].read() == f.read()
                    assert mocked.call_args[1]['files']['file'][2] == 'application/json'


@pytest.mark.parametrize('sample,is_sample', [(None, False), ('true', True)])
@pytest.mark.parametrize('note', ['', 'Started by NAME.'])
@pytest.mark.parametrize('encoding,encoding2', [(None, 'utf-8'), ('iso-8859-1', 'iso-8859-1')])
@pytest.mark.parametrize('ok', [True, False])
def test_item_scraped_file_item(sample, is_sample, note, encoding, encoding2, ok, tmpdir, caplog):
    spider = spider_with_files_store(tmpdir, sample=sample, note=note)

    api_extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    with patch('requests.post') as mocked:
        response = Mock()
        response.ok = ok
        response.status_code = 400
        mocked.return_value = response

        kwargs = {}
        if encoding:
            kwargs['encoding'] = encoding
        item = spider.build_file_item(
            number=1,
            file_name='data.json',
            url='https://example.com/remote.json',
            data=b'{"key": "value"}',
            data_type='release_package',
            encoding=encoding2,
        )

        api_extension.item_scraped(item, spider)

        if not ok:
            message = 'Failed to post [https://example.com/remote.json]. API status code: 400'

            assert len(caplog.records) == 1
            assert caplog.records[0].name == 'test'
            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].message == message

        expected = {
            'collection_source': 'test',
            'collection_data_version': '2001-02-03 04:05:06',
            'collection_sample': is_sample,
            'file_name': 'data.json',
            'url': 'https://example.com/remote.json',
            # Specific to this test case.
            'data_type': 'release_package',
            'encoding': encoding2,
            'number': 1,
            'data': b'{"key": "value"}',
        }
        if note:
            expected['collection_note'] = note

        mocked.assert_called_once_with(
            'http://httpbin.org/anything/api/v1/submit/item/',
            headers={
                'Authorization': 'ApiKey xxx',
            },
            proxies={
                'http': None,
                'https': None,
            },
            data=expected,
        )


@pytest.mark.parametrize('sample,is_sample', [(None, False), ('true', True)])
@pytest.mark.parametrize('ok', [True, False])
def test_item_scraped_file_error(sample, is_sample, ok, tmpdir, caplog):
    spider = spider_with_files_store(tmpdir, sample=sample)

    api_extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    with patch('requests.post') as mocked:
        response = Mock()
        response.ok = ok
        response.status_code = 400
        mocked.return_value = response

        data = FileError({
            'file_name': 'file.json',
            'url': 'https://example.com/remote.json',
            'errors': {'http_code': 500},
        })

        api_extension.item_scraped(data, spider)

        if not ok:
            message = 'Failed to post [https://example.com/remote.json]. File Errors API status code: 400'

            assert len(caplog.records) == 1
            assert caplog.records[0].name == 'test'
            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].message == message

        expected = {
            'collection_source': 'test',
            'collection_data_version': '2001-02-03 04:05:06',
            'collection_sample': is_sample,
            'file_name': 'file.json',
            'url': 'https://example.com/remote.json',
            # Specific to this test case.
            'errors': '{"http_code": 500}',
        }

        mocked.assert_called_once_with(
            'http://httpbin.org/anything/api/v1/submit/file_errors/',
            headers={
                'Authorization': 'ApiKey xxx',
            },
            proxies={
                'http': None,
                'https': None,
            },
            data=expected,
        )


@pytest.mark.parametrize('sample,is_sample', [(None, False), ('true', True)])
@pytest.mark.parametrize('ok', [True, False])
def test_spider_closed(sample, is_sample, ok, tmpdir, caplog):
    spider = spider_with_files_store(tmpdir, sample=sample)

    api_extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    with patch('requests.post') as mocked:
        response = Mock()
        response.ok = ok
        response.status_code = 400
        mocked.return_value = response

        api_extension.spider_closed(spider, 'finished')

        mocked.assert_called_once_with(
            'http://httpbin.org/anything/api/v1/submit/end_collection_store/',
            headers={
                'Authorization': 'ApiKey xxx',
            },
            proxies={
                'http': None,
                'https': None,
            },
            data={
                'collection_source': 'test',
                'collection_data_version': '2001-02-03 04:05:06',
                'collection_sample': is_sample,
            },
        )

        if not ok:
            assert len(caplog.records) == 1
            assert caplog.records[0].name == 'test'
            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].message == 'Failed to post End Collection Store. API status code: 400'


def test_spider_closed_other_reason(tmpdir):
    spider = spider_with_files_store(tmpdir)

    api_extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    with patch('requests.post') as mocked:
        api_extension.spider_closed(spider, 'xxx')

        mocked.assert_not_called()


@pytest.mark.parametrize('sample,path', [
    (None, os.path.join('test', '20010203_040506', 'file.json')),
    ('true', os.path.join('test_sample', '20010203_040506', 'file.json')),
])
def test_item_scraped_with_build_file_from_response(sample, path, tmpdir):
    spider = spider_with_files_store(tmpdir, sample=sample)
    store_extension = KingfisherFilesStore.from_crawler(spider.crawler)

    response = Mock()
    response.body = b'{"key": "value"}'
    response.request = Mock()
    response.request.url = 'https://example.com/remote.json'

    item = spider.build_file_from_response(response, file_name='file.json', data_type='release_package',
                                           encoding='iso-8859-1')
    store_extension.item_scraped(item, spider)

    with open(tmpdir.join(path)) as f:
        assert f.read() == '{"key": "value"}'

    with open(tmpdir.join(path + '.fileinfo')) as f:
        assert json.load(f) == {
            'url': 'https://example.com/remote.json',
            'data_type': 'release_package',
            'encoding': 'iso-8859-1',
        }

    assert item['path'] == path
    assert item['files_store'] == tmpdir


@pytest.mark.parametrize('sample,path', [
    (None, os.path.join('test', '20010203_040506', 'file.json')),
    ('true', os.path.join('test_sample', '20010203_040506', 'file.json')),
])
def test_item_scraped_with_build_file(sample, path, tmpdir):
    spider = spider_with_files_store(tmpdir, sample=sample)
    store_extension = KingfisherFilesStore.from_crawler(spider.crawler)

    data = b'{"key": "value"}'
    url = 'https://example.com/remote.json'

    item = spider.build_file(file_name='file.json', url=url, data=data, data_type='release_package',
                             encoding='iso-8859-1')
    store_extension.item_scraped(item, spider)

    with open(tmpdir.join(path)) as f:
        assert f.read() == '{"key": "value"}'

    with open(tmpdir.join(path + '.fileinfo')) as f:
        assert json.load(f) == {
            'url': 'https://example.com/remote.json',
            'data_type': 'release_package',
            'encoding': 'iso-8859-1',
        }

    assert item['path'] == path
    assert item['files_store'] == tmpdir


def test_build_file_with_existing_directory():
    spider = spider_with_crawler()

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store
        store_extension = KingfisherFilesStore.from_crawler(spider.crawler)
        os.makedirs(os.path.join(files_store, 'test', '20010203_040506'))

        # No FileExistsError exception.
        store_extension.item_scraped(spider.build_file(file_name='file.json', data=b'{"key": "value"}'), spider)


def test_item_scraped_latest_date():
    with TemporaryDirectory() as tmpdirname:
        spider = spider_with_files_store(tmpdirname, latest=True)
        spider.crawler.settings['KINGFISHER_LATEST_RELEASE_DATE_FILE_PATH'] = tmpdirname

        latest_extension = KingfisherLatestDate.from_crawler(spider.crawler)
        item = LatestReleaseDateItem({'date': '2020-10-01T00:00:00Z'})
        latest_extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, 'latest_dates.csv')) as f:
            assert 'test,2020-10-01T00:00:00Z\n' == f.read()

        # the same item is processed just once
        latest_extension.item_scraped(item, spider)

        with open(os.path.join(tmpdirname, 'latest_dates.csv')) as f:
            assert 'test,2020-10-01T00:00:00Z\n' == f.read()

        # a non processed item is marked as an error
        spider.name = 'no date'

        latest_extension.spider_closed(spider, 'itemcount')

        with open(os.path.join(tmpdirname, 'latest_dates.csv')) as f:
            assert 'test,2020-10-01T00:00:00Z\nno date,itemcount\n' == f.read()
