import json
import os.path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
from zipfile import ZipFile

import pytest
from scrapy.http import TextResponse

from kingfisher_scrapy.base_spider import BaseSpider, LinksSpider, ZipSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.items import File, FileError, FileItem
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


def test_build_file_from_response():
    spider = BaseSpider(name='test')

    response = Mock()
    response.body = b'{"key": "value"}'
    response.request = Mock()
    response.request.url = 'https://example.com/remote.json'

    actual = spider.build_file_from_response(response, 'file.json', data_type='release_package', encoding='iso-8859-1')

    assert actual == File({
        'file_name': 'file.json',
        'data': b'{"key": "value"}',
        "data_type": 'release_package',
        "url": 'https://example.com/remote.json',
        'encoding': 'iso-8859-1',
        'post_to_api': True,
    })


def test_build_file():
    spider = BaseSpider(name='test')

    data = b'{"key": "value"}'
    url = 'https://example.com/remote.json'

    actual = spider.build_file(data, 'file.json', url=url, data_type='release_package', encoding='iso-8859-1')

    assert actual == File({
        'file_name': 'file.json',
        'data': b'{"key": "value"}',
        "data_type": 'release_package',
        "url": 'https://example.com/remote.json',
        'encoding': 'iso-8859-1',
        'post_to_api': True,
    })


def test_next_link():
    spider = spider_with_crawler(spider_class=LinksSpider)

    url = 'https://example.com/remote.json'
    text_response = TextResponse('test')
    response = text_response.replace(body='{"links": {"next": "' + url + '"}}')

    actual = spider.next_link(response)

    assert actual.url == url


def test_parse_next_link_404():
    spider = spider_with_crawler(spider_class=LinksSpider)

    response = TextResponse('test')
    response.status = 404
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test'}
    response.request.url = 'url'

    actual = spider.parse_next_link(response, None).__next__()

    assert isinstance(actual, FileError)


def test_parse_next_link_200():
    spider = spider_with_crawler(spider_class=LinksSpider)

    url = 'https://example.com/remote.json'
    text_response = TextResponse('test')

    response = text_response.replace(body='{"links": {"next": "' + url + '"}}')
    response.status = 200
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test'}
    response.request.url = 'url'

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store
        os.makedirs(os.path.join(files_store, 'test', '20010203_040506'))

        actual = spider.parse_next_link(response, None).__next__()

        assert isinstance(actual, File)
        assert actual['file_name'] == 'test'
        for item in spider.parse_next_link(response, None):
            assert item


def test_parse_zipfile_404():
    spider = spider_with_crawler(spider_class=ZipSpider)

    response = TextResponse('test')
    response.status = 404
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test'}
    response.request.url = 'url'

    actual = spider.parse_zipfile(response, None).__next__()

    assert isinstance(actual, FileError)


def test_parse_zipfile_200():
    spider = spider_with_crawler(spider_class=ZipSpider)

    response = TextResponse('test')
    response.status = 200
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test.json'}
    response.request.url = 'url'

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store
        tmp = os.path.join(files_store, 'test', '20010203_040506')
        os.makedirs(tmp)

        with open(os.path.join(tmp, 'test'), 'w'):
            pass
        with ZipFile(os.path.join(tmp, 'test.zip'), 'w') as z:
            z.write(os.path.join(tmp, 'test'))
        with open(os.path.join(tmp, 'test.zip'), 'rb') as z:
            response = response.replace(body=z.read())

        actual = spider.parse_zipfile(response, None).__next__()

        assert isinstance(actual, File)
        assert actual['file_name'].find('.json')


def test_parse_zipfile_json_lines():
    spider = spider_with_crawler(spider_class=ZipSpider)

    response = TextResponse('test')
    response.status = 200
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test.json'}
    response.request.url = 'url'

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store
        tmp = os.path.join(files_store, 'test', '20010203_040506')
        os.makedirs(tmp)

        with open(os.path.join(tmp, 'test.json'), 'w') as f:
            for i in range(10):
                f.write('{"key": "value"}\n')
        with ZipFile(os.path.join(tmp, 'test.zip'), 'w') as z:
            z.write(os.path.join(tmp, 'test.json'))
        with open(os.path.join(tmp, 'test.zip'), 'rb') as z:
            response = response.replace(body=z.read())

        actual = spider.parse_zipfile(response, None, file_format='json_lines').__next__()

        assert isinstance(actual, FileItem)
        assert actual['number'] == 1

        spider.sample = True
        total = 0
        for item in spider.parse_zipfile(response, None, file_format='json_lines'):
            total = total + 1
            assert isinstance(item, FileItem)
            assert item['number'] == total
        assert total == 10


def test_parse_zipfile_release_package():
    spider = spider_with_crawler(spider_class=ZipSpider)

    response = TextResponse('test')
    response.status = 200
    response.request = Mock()
    response.request.meta = {'kf_filename': 'test.json'}
    response.request.url = 'url'

    with TemporaryDirectory() as tmpdirname:
        files_store = os.path.join(tmpdirname, 'data')
        spider.crawler.settings['FILES_STORE'] = files_store
        tmp = os.path.join(files_store, 'test', '20010203_040506')
        os.makedirs(tmp)

        with open(os.path.join(tmp, 'test.json'), 'w') as f:
            release = {'releases': [], 'publisher': {'name': 'test'},
                       'extensions': ['a', 'b'], 'license': 'test', 'extra': 1.1}
            for i in range(110):
                release['releases'].append({'key': 'value'})
            json.dump(release, f)
        with ZipFile(os.path.join(tmp, 'test.zip'), 'w') as z:
            z.write(os.path.join(tmp, 'test.json'))
        with open(os.path.join(tmp, 'test.zip'), 'rb') as z:
            response = response.replace(body=z.read())

        actual = spider.parse_zipfile(response, None, file_format='release_package').__next__()
        data = json.loads(actual['data'])

        assert isinstance(actual, FileItem)
        assert actual['number'] == 1
        assert data['publisher']['name'] == 'test'
        assert data['extensions'] == ['a', 'b']
        assert len(data['releases']) == spider.MAX_RELEASES_PER_PACKAGE

        spider.sample = True
        total = 0
        for item in spider.parse_zipfile(response, None, file_format='release_package'):
            total = total + 1
            data = json.loads(item['data'])
            assert isinstance(item, FileItem)
            assert item['number'] == total
            assert len(data['releases']) == spider.MAX_SAMPLE
        assert total == 1


def test_date_arguments():
    test_date = '2000-01-01'
    error_message = "time data 'test' does not match format '%Y-%m-%d'"

    assert spider_with_crawler(from_date=test_date)
    with pytest.raises(SpiderArgumentError) as e:
        assert spider_with_crawler(from_date='test')
    assert str(e.value) == 'spider argument from_date: invalid date value: {}'.format(error_message)

    assert spider_with_crawler(until_date=test_date, default_from_date=test_date)
    with pytest.raises(SpiderArgumentError) as e:
        assert spider_with_crawler(until_date='test', default_from_date=test_date)
    assert str(e.value) == 'spider argument until_date: invalid date value: {}'.format(error_message)
