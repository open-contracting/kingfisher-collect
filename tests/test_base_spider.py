import json
import os.path
import re
from datetime import datetime
from tempfile import TemporaryDirectory
from unittest.mock import Mock

import pytest
from scrapy.http.response import text

from kingfisher_scrapy.base_spider import BaseSpider, LinksSpider
from tests import spider_with_crawler


@pytest.mark.parametrize('sample,expected', [
    ('true', True),
    ('false', False),
    (True, False),
    (False, False),
    (None, False),
])
def test_sample(sample, expected):
    spider = BaseSpider(name='test', sample=sample)

    assert spider.sample == expected


def test_sample_no_kwarg():
    spider = BaseSpider(name='test')

    assert spider.sample is False


@pytest.mark.parametrize('sample,expected', [
    (None, 'data/test/20010203_040506/file.json'),
    ('true', 'data/test_sample/20010203_040506/file.json'),
])
def test_get_local_file_path_including_filestore(sample, expected):
    spider = spider_with_crawler(sample=sample)
    spider.crawler.settings['FILES_STORE'] = 'data'

    assert spider.get_local_file_path_including_filestore('file.json') == expected


@pytest.mark.parametrize('sample,expected', [
    (None, 'test/20010203_040506/file.json'),
    ('true', 'test_sample/20010203_040506/file.json'),
])
def test_get_local_file_path_excluding_filestore(sample, expected):
    spider = spider_with_crawler(sample=sample)

    assert spider.get_local_file_path_excluding_filestore('file.json') == expected


@pytest.mark.parametrize('sample,is_sample,path', [
    (None, False, 'test/20010203_040506/kingfisher.collectioninfo'),
    ('true', True, 'test_sample/20010203_040506/kingfisher.collectioninfo'),
])
@pytest.mark.parametrize('note', ['', 'Started by NAME.'])
def test_spider_opened(sample, is_sample, path, note):
    spider = spider_with_crawler(sample=sample, note=note)

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


@pytest.mark.parametrize('sample,path', [
    (None, 'test/20010203_040506/kingfisher-finished.collectioninfo'),
    ('true', 'test_sample/20010203_040506/kingfisher-finished.collectioninfo'),
])
def test_spider_closed(sample, path):
    spider = spider_with_crawler(sample=sample)

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
    spider = spider_with_crawler(sample=sample)

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
    spider = spider_with_crawler(sample=sample)

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


def test_next_link():
    url = 'https://example.com/remote.json'
    text_response = text.TextResponse('test')
    response = text_response.replace(body='{"links": {"next": "' + url + '"}}')

    spider = LinksSpider()
    actual = spider.next_link(response)

    assert actual.url == url
