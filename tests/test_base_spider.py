import json
import os.path
from tempfile import TemporaryDirectory
from unittest.mock import Mock

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
