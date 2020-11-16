import os
from unittest.mock import Mock, patch

import pytest
from scrapy.exceptions import NotConfigured

from kingfisher_scrapy.extensions import KingfisherFilesStore, KingfisherProcessAPI
from kingfisher_scrapy.items import FileError
from tests import spider_with_crawler, spider_with_files_store


def test_from_crawler():
    spider = spider_with_crawler()
    spider.crawler.settings['KINGFISHER_API_URI'] = 'http://httpbin.org/anything'
    spider.crawler.settings['KINGFISHER_API_KEY'] = 'xxx'
    spider.crawler.settings['KINGFISHER_API_LOCAL_DIRECTORY'] = 'localdir'

    extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    assert extension.directory == 'localdir'


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
@pytest.mark.parametrize('crawl_time', [None, '2020-01-01T00:00:00'])
def test_item_scraped_file(sample, is_sample, path, note, encoding, encoding2, directory, ok, post_to_api,
                           crawl_time, tmpdir, caplog):
    spider = spider_with_files_store(tmpdir, sample=sample, note=note,
                                     crawl_time=crawl_time)

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

    with patch('treq.post') as mocked:
        response = Mock()
        response.code = 400
        mocked.return_value = response

        api_extension.item_scraped(item, spider)

        if not ok:
            if not post_to_api:
                assert len(caplog.records) == 0
            else:
                message = 'create_file failed (https://example.com/remote.json) with status code: 400'

                assert len(caplog.records) == 1
                assert caplog.records[0].name == 'test'
                assert caplog.records[0].levelname == 'WARNING'
                assert caplog.records[0].message == message

        expected = {
            'collection_source': 'test',
            'collection_data_version': '2001-02-03 04:05:06',
            'collection_sample': str(is_sample),
            'file_name': 'file.json',
            'url': 'https://example.com/remote.json',
            # Specific to this test case.
            'data_type': 'release_package',
            'encoding': encoding2,
        }
        if note:
            expected['collection_note'] = note
        if crawl_time:
            expected['collection_data_version'] = '2020-01-01 00:00:00'
            path = path.replace('20010203_040506', '20200101_000000')
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
                assert len(mocked.call_args[1]) == 3

                if directory:
                    assert mocked.call_args[1]['files'] == {}
                else:
                    assert len(mocked.call_args[1]['files']) == 1
                    assert len(mocked.call_args[1]['files']['file']) == 3
                    assert mocked.call_args[1]['files']['file'][0] == 'file.json'
                    assert mocked.call_args[1]['files']['file'][1] == 'application/json'
                    assert mocked.call_args[1]['files']['file'][2].read() == f.read()


@pytest.mark.parametrize('sample,is_sample', [(None, False), ('true', True)])
@pytest.mark.parametrize('note', ['', 'Started by NAME.'])
@pytest.mark.parametrize('encoding,encoding2', [(None, 'utf-8'), ('iso-8859-1', 'iso-8859-1')])
@pytest.mark.parametrize('ok', [True, False])
def test_item_scraped_file_item(sample, is_sample, note, encoding, encoding2, ok, tmpdir, caplog):
    spider = spider_with_files_store(tmpdir, sample=sample, note=note)

    extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    with patch('treq.post') as mocked:
        response = Mock()
        response.code = 400
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

        extension.item_scraped(item, spider)

        if not ok:
            message = 'create_file_item failed (https://example.com/remote.json) with status code: 400'

            assert len(caplog.records) == 1
            assert caplog.records[0].name == 'test'
            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].message == message

        expected = {
            'collection_source': 'test',
            'collection_data_version': '2001-02-03 04:05:06',
            'collection_sample': str(is_sample),
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
            data=expected,
        )


@pytest.mark.parametrize('sample,is_sample', [(None, False), ('true', True)])
@pytest.mark.parametrize('ok', [True, False])
def test_item_scraped_file_error(sample, is_sample, ok, tmpdir, caplog):
    spider = spider_with_files_store(tmpdir, sample=sample)

    extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    with patch('treq.post') as mocked:
        response = Mock()
        response.code = 400
        mocked.return_value = response

        data = FileError({
            'file_name': 'file.json',
            'url': 'https://example.com/remote.json',
            'errors': {'http_code': 500},
        })

        extension.item_scraped(data, spider)

        if not ok:
            message = 'create_file_error failed (https://example.com/remote.json) with status code: 400'

            assert len(caplog.records) == 1
            assert caplog.records[0].name == 'test'
            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].message == message

        expected = {
            'collection_source': 'test',
            'collection_data_version': '2001-02-03 04:05:06',
            'collection_sample': str(is_sample),
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
            data=expected,
        )


@pytest.mark.parametrize('sample,is_sample', [(None, False), ('true', True)])
@pytest.mark.parametrize('ok', [True, False])
def test_spider_closed(sample, is_sample, ok, tmpdir, caplog):
    spider = spider_with_files_store(tmpdir, sample=sample)

    extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    with patch('treq.post') as mocked:
        response = Mock()
        response.code = 400
        mocked.return_value = response

        extension.spider_closed(spider, 'finished')

        mocked.assert_called_once_with(
            'http://httpbin.org/anything/api/v1/submit/end_collection_store/',
            headers={
                'Authorization': 'ApiKey xxx',
            },
            data={
                'collection_source': 'test',
                'collection_data_version': '2001-02-03 04:05:06',
                'collection_sample': str(is_sample),
            },
        )

        if not ok:
            assert len(caplog.records) == 1
            assert caplog.records[0].name == 'test'
            assert caplog.records[0].levelname == 'WARNING'
            assert caplog.records[0].message == 'end_collection_store failed (test) with status code: 400'


def test_spider_closed_other_reason(tmpdir):
    spider = spider_with_files_store(tmpdir)

    extension = KingfisherProcessAPI.from_crawler(spider.crawler)

    with patch('treq.post') as mocked:
        extension.spider_closed(spider, 'xxx')

        mocked.assert_not_called()
