import json
import os.path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
from zipfile import ZipFile

import pytest
from scrapy.http.response import text

from kingfisher_scrapy.base_spider import BaseSpider, LinksSpider, ZipSpider
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
    url = 'https://example.com/remote.json'
    text_response = text.TextResponse('test')
    response = text_response.replace(body='{"links": {"next": "' + url + '"}}')
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
        for item in spider.parse_next_link(response, None):
            assert item


def test_parse_zipfile_404():
    response = text.TextResponse('test')
    response.status = 404
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test'}
    response.request.url = 'url'
    spider = spider_with_crawler(spider_class=ZipSpider)
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

        open(tmp + "test", "w").close()
        with ZipFile(tmp + '/test.zip', 'w') as z:
            z.write(tmp + "test")
        with open(tmp + '/test.zip', 'rb') as z:
            response = response.replace(body=z.read())

        spider = spider_with_crawler(spider_class=ZipSpider)
        spider.crawler.settings['FILES_STORE'] = files_store
        actual = spider.parse_zipfile(response, None).__next__()
        assert actual['success'] is True and actual['file_name'].find('.json')


def test_parse_zipfile_json_lines():
    response = text.TextResponse('test')
    response.status = 200
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test.json'}
    response.request.url = 'url'
    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        tmp = os.path.join(files_store, 'test/20010203_040506')
        os.makedirs(tmp)
        with open(tmp + "test.json", 'w') as f:
            for i in range(10):
                f.write('{"key": "value"}\n')
        with ZipFile(tmp + '/test.zip', 'w') as z:
            z.write(tmp + "test.json")
        with open(tmp + '/test.zip', 'rb') as z:
            response = response.replace(body=z.read())
        spider = spider_with_crawler(spider_class=ZipSpider)
        spider.crawler.settings['FILES_STORE'] = files_store
        actual = spider.parse_zipfile(response, None, file_format='json_lines').__next__()
        assert actual['success'] is True and actual['number'] == 1
        spider.sample = True
        total = 0
        for item in spider.parse_zipfile(response, None, file_format='json_lines'):
            total = total + 1
            assert item['success'] is True and item['number'] == total
        assert total == 10


def test_parse_zipfile_release_package():
    response = text.TextResponse('test')
    response.status = 200
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test.json'}
    response.request.url = 'url'
    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        tmp = os.path.join(files_store, 'test/20010203_040506')
        os.makedirs(tmp)
        with open(tmp + "test.json", 'w') as f:
            release = {'releases': [], 'publisher': {'name': 'test'},
                       'extensions': ['a', 'b'], 'license': 'test', 'extra': 1.1}
            for i in range(110):
                release['releases'].append({'key': 'value'})
            json.dump(release, f)
        with ZipFile(tmp + '/test.zip', 'w') as z:
            z.write(tmp + "test.json")
        with open(tmp + '/test.zip', 'rb') as z:
            response = response.replace(body=z.read())
        spider = spider_with_crawler(spider_class=ZipSpider)
        spider.crawler.settings['FILES_STORE'] = files_store
        actual = spider.parse_zipfile(response, None, file_format='release_package').__next__()
        data = json.loads(actual['data'])
        assert actual['success'] is True and actual['number'] == 1
        assert data['publisher']['name'] == 'test'
        assert data['extensions'] == ['a', 'b']
        assert len(data['releases']) == spider.MAX_RELEASES_PER_PACKAGE
        spider.sample = True
        total = 0
        for item in spider.parse_zipfile(response, None, file_format='release_package'):
            total = total + 1
            data = json.loads(item['data'])
            assert item['success'] is True and item['number'] == total
            assert len(data['releases']) == spider.MAX_SAMPLE
        assert total == 1


def test_date_arguments():
    test_date = '2000-01-01'
    error_message = "time data 'test' does not match format '%Y-%m-%d'"

    assert spider_with_crawler(from_date=test_date)

    assert spider_with_crawler(until_date=test_date, default_from_date=test_date)

    with pytest.raises(SpiderArgumentError) as e:
        assert spider_with_crawler(from_date='test')

    assert str(e.value) == 'spider argument from_date: invalid date value: {}'.format(error_message)

    with pytest.raises(SpiderArgumentError) as e:
        assert spider_with_crawler(until_date='test', default_from_date=test_date)

    assert str(e.value) == 'spider argument until_date: invalid date value: {}'.format(error_message)
