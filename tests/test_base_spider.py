import json
import os.path
import re
from datetime import datetime
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import pytest

from kingfisher_scrapy.base_spider import BaseSpider
from tests import spider_with_crawler


@pytest.mark.parametrize('sample,expected', [
    ('true', True),
    ('false', False),
    (True, False),
    (False, False),
    (None, False),
])
def test_is_sample(sample, expected):
    spider = BaseSpider('test')
    spider.sample = sample

    assert spider.is_sample() == expected


def test_is_sample_no_hasattr():
    spider = BaseSpider('test')

    assert spider.is_sample() is False


@pytest.mark.parametrize('sample,expected', [
    (None, 'data/test/20010203_040506/file.json'),
    ('true', 'data/test_sample/20010203_040506/file.json'),
])
def test_get_local_file_path_including_filestore(sample, expected):
    spider = spider_with_crawler(sample)
    spider.crawler.settings['FILES_STORE'] = 'data'

    assert spider.get_local_file_path_including_filestore('file.json') == expected


@pytest.mark.parametrize('sample,expected', [
    (None, 'test/20010203_040506/file.json'),
    ('true', 'test_sample/20010203_040506/file.json'),
])
def test_get_local_file_path_excluding_filestore(sample, expected):
    spider = spider_with_crawler(sample)

    assert spider.get_local_file_path_excluding_filestore('file.json') == expected


@pytest.mark.parametrize('sample,is_sample,note,path', [
    (None, False, '', 'test/20010203_040506/kingfisher.collectioninfo'),
    (None, False, 'Started by NAME.', 'test/20010203_040506/kingfisher.collectioninfo'),
    ('true', True, '', 'test_sample/20010203_040506/kingfisher.collectioninfo'),
    ('true', True, 'Started by NAME.', 'test_sample/20010203_040506/kingfisher.collectioninfo'),
])
def test_spider_opened(sample, is_sample, note, path):
    spider = spider_with_crawler(sample)
    spider.note = note

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store

        spider.spider_opened(spider)

        expected = {
            'source': 'test',
            'data_version': '20010203_040506',
            'sample': is_sample,
        }
        if note:
            expected['note'] = note
        with open(os.path.join(files_store, path)) as f:
            assert json.load(f) == expected


def test_spider_opened_with_existing_directory():
    spider = spider_with_crawler()

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store
        os.makedirs(os.path.join(files_store, 'test/20010203_040506'))

        spider.spider_opened(spider)  # no FileExistsError exception


@pytest.mark.parametrize('sample,is_sample,ok,path', [
    (None, False, False, 'test/20010203_040506/kingfisher-finished.collectioninfo'),
    (None, False, True, 'test/20010203_040506/kingfisher-finished.collectioninfo'),
    ('true', True, False, 'test_sample/20010203_040506/kingfisher-finished.collectioninfo'),
    ('true', True, True, 'test_sample/20010203_040506/kingfisher-finished.collectioninfo'),
])
def test_spider_closed_with_api(sample, is_sample, ok, path, caplog):
    spider = spider_with_crawler(sample)

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store
        spider.crawler.settings['KINGFISHER_API_URI'] = 'http://httpbin.org/anything'
        spider.crawler.settings['KINGFISHER_API_KEY'] = 'xxx'

        with patch('requests.post') as mocked:
            response = Mock()
            response.ok = ok
            response.status_code = 500
            mocked.return_value = response

            spider.spider_opened(spider)
            spider.spider_closed(spider, 'finished')

            now = datetime.now().strftime('%Y-%m-%d %H:')
            with open(os.path.join(files_store, path)) as f:
                data = json.load(f)
                assert len(data) == 1
                assert re.match(now + r'\d\d:\d\d\Z', data['at'])
            mocked.assert_called_once_with(
                'http://httpbin.org/anything/api/v1/submit/end_collection_store/',
                headers={
                    'Authorization': 'ApiKey xxx',
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
                assert caplog.records[0].message == 'Failed to post End Collection Store. API status code: 500'


@pytest.mark.parametrize('sample,path', [
    (None, 'test/20010203_040506/kingfisher-finished.collectioninfo'),
    ('true', 'test_sample/20010203_040506/kingfisher-finished.collectioninfo'),
])
def test_spider_closed_without_api(sample, path):
    spider = spider_with_crawler(sample)

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store

        spider.spider_opened(spider)
        spider.spider_closed(spider, 'finished')

        now = datetime.now().strftime('%Y-%m-%d %H:')
        with open(os.path.join(files_store, path)) as f:
            data = json.load(f)
            assert len(data) == 1
            assert re.match(now + r'\d\d:\d\d\Z', data['at'])


def test_spider_closed_other_reason():
    spider = spider_with_crawler()

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store

        spider.spider_closed(spider, 'xxx')

        assert not os.path.exists(os.path.join(files_store))


@pytest.mark.parametrize('sample,path', [
    (None, 'test/20010203_040506/file.json'),
    ('true', 'test_sample/20010203_040506/file.json'),
])
def test_save_response_to_disk(sample, path):
    spider = spider_with_crawler(sample)

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store

        response = Mock()
        response.body = b'{"key": "value"}'
        response.request = Mock()
        response.request.url = 'https://example.com/remote.json'

        actual = spider.save_response_to_disk(response, 'file.json', data_type='release_package',
                                              encoding='iso-8859-1')

        with open(os.path.join(files_store, path)) as f:
            assert f.read() == '{"key": "value"}'
        with open(os.path.join(files_store, path + '.fileinfo')) as f:
            assert json.load(f) == {
                'url': 'https://example.com/remote.json',
                'data_type': 'release_package',
                'encoding': 'iso-8859-1',
            }
        assert actual == {
            'success': True,
            'file_name': 'file.json',
            "data_type": 'release_package',
            "url": 'https://example.com/remote.json',
            'encoding': 'iso-8859-1',
        }


@pytest.mark.parametrize('sample,path', [
    (None, 'test/20010203_040506/file.json'),
    ('true', 'test_sample/20010203_040506/file.json'),
])
def test_save_data_to_disk(sample, path):
    spider = spider_with_crawler(sample)

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store

        data = b'{"key": "value"}'
        url = 'https://example.com/remote.json'

        actual = spider.save_data_to_disk(data, 'file.json', url=url, data_type='release_package',
                                          encoding='iso-8859-1')

        with open(os.path.join(files_store, path)) as f:
            assert f.read() == '{"key": "value"}'
        with open(os.path.join(files_store, path + '.fileinfo')) as f:
            assert json.load(f) == {
                'url': 'https://example.com/remote.json',
                'data_type': 'release_package',
                'encoding': 'iso-8859-1',
            }
        assert actual == {
            'success': True,
            'file_name': 'file.json',
            "data_type": 'release_package',
            "url": 'https://example.com/remote.json',
            'encoding': 'iso-8859-1',
        }


def test_save_data_to_disk_with_existing_directory():
    spider = spider_with_crawler()

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store
        os.makedirs(os.path.join(files_store, 'test/20010203_040506'))

        spider.save_data_to_disk(b'{"key": "value"}', 'file.json')  # no FileExistsError exception
