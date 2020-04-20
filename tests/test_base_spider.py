import json
import os.path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
from zipfile import ZipFile

import pytest
from scrapy.http.response import text

from kingfisher_scrapy.base_spider import BaseSpider, LinksSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
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


def test_next_link():
    url = 'https://example.com/remote.json'
    text_response = text.TextResponse('test')
    response = text_response.replace(body='{"links": {"next": "' + url + '"}}')

    spider = spider_with_crawler(spider_class=LinksSpider)
    actual = spider.next_link(response)

    assert actual.url == url


def test_parse_next_link_404():
    response = text.TextResponse('test')
    response.status = 404
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test'}
    response.request.url = 'url'
    spider = spider_with_crawler(spider_class=LinksSpider)
    actual = spider.parse_next_link(response, None).__next__()
    assert actual['success'] is False


def test_parse_next_link_200():
    response = text.TextResponse('test')
    response.status = 200
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test'}
    response.request.url = 'url'
    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        os.makedirs(os.path.join(files_store, 'test/20010203_040506'))
        spider = spider_with_crawler(spider_class=LinksSpider)
        spider.crawler.settings['FILES_STORE'] = files_store
        actual = spider.parse_next_link(response, None).__next__()
        assert actual['success'] is True and actual['file_name'] == 'test'


def test_parse_zipfile_404():
    response = text.TextResponse('test')
    response.status = 404
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test'}
    response.request.url = 'url'
    spider = spider_with_crawler(spider_class=BaseSpider)
    actual = spider.parse_zipfile(response, None).__next__()
    assert actual['success'] is False


def test_parse_zipfile_200():
    response = text.TextResponse('test')
    response.status = 200
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test.json'}
    response.request.url = 'url'
    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        tmp = os.path.join(files_store, 'test/20010203_040506')
        os.makedirs(tmp)

        open(tmp + "test.json", "w").close()
        with ZipFile(tmp + '/test.zip', 'w') as z:
            z.write(tmp + "test.json")
        with open(tmp + '/test.zip', 'rb') as z:
            response = response.replace(body=z.read())

        spider = spider_with_crawler(spider_class=BaseSpider)
        spider.crawler.settings['FILES_STORE'] = files_store
        actual = spider.parse_zipfile(response, None).__next__()
        assert actual['success'] is True and actual['file_name'].find('.json')


def test_date_arguments():
    test_date = '2000-01-01'
    exception_message = "time data 'test' does not match format '%Y-%m-%d'"

    assert spider_with_crawler(from_date=test_date)

    assert spider_with_crawler(until_date=test_date, default_from_date=test_date)

    with pytest.raises(Exception) as e:
        assert spider_with_crawler(from_date='test')
    assert str(e.value) == exception_message


def test_exceptions():
    exception_message = ''
    with pytest.raises(Exception) as e:
        raise SpiderArgumentError()
    assert str(e.value) == exception_message

