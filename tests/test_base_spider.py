from unittest.mock import Mock

import pytest
import scrapy
from scrapy.http import TextResponse

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.items import File
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


@pytest.mark.parametrize('status,expected', [(100, False), (200, True), (204, True), (300, False), (500, False)])
def test_is_http_success(status, expected):
    spider = BaseSpider(name='test')

    response = TextResponse('http://example.com', status=status)

    assert spider.is_http_success(response) == expected


def test_build_file_from_response():
    spider = BaseSpider(name='test')

    response = Mock()
    response.body = b'{"key": "value"}'
    response.request = Mock()
    response.request.url = 'https://example.com/remote.json'
    response.request.meta = {'file_name': 'file.json'}

    actual = spider.build_file_from_response(response, file_name='file.json', data_type='release_package',
                                             encoding='iso-8859-1')

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

    actual = spider.build_file(file_name='file.json', url=url, data=data, data_type='release_package',
                               encoding='iso-8859-1')

    assert actual == File({
        'file_name': 'file.json',
        'data': b'{"key": "value"}',
        "data_type": 'release_package',
        "url": 'https://example.com/remote.json',
        'encoding': 'iso-8859-1',
        'post_to_api': True,
    })


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


def test_custom_collection_data_version():
    error_message = "time data '2020' does not match format '%Y-%m-%dT%H:%M:%S'"

    assert spider_with_crawler(crawl_time='2020-01-01T00:00:00')
    with pytest.raises(SpiderArgumentError) as e:
        assert spider_with_crawler(crawl_time='2020')
    assert str(e.value) == 'spider argument crawl_time: invalid date value: {}'.format(
        error_message)


@pytest.mark.parametrize('kwargs,expected', [
    ({'qs:param1': 'val1'}, '?param1=val1'),
    ({'qs:param1': 'val1', 'qs:param2': 'val2'}, '?param1=val1&param2=val2'),
    ({'qs:param1': 'val1', 'qs:param2': 'Ministerio de Urbanismo, Vivienda y Habitat'},
     '?param1=val1&param2=Ministerio+de+Urbanismo%2C+Vivienda+y+Habitat')
])
def test_qs_parameters(kwargs, expected):
    test_spider = type('TestSpider', (BaseSpider,), {
        'start_requests': lambda _self: [scrapy.Request('http://example.com')]
    })
    spider = spider_with_crawler(test_spider, **kwargs)

    for request in spider.start_requests():
        assert expected in request.url
