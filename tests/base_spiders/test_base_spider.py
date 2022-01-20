from unittest.mock import Mock

import pytest
import scrapy
from scrapy.http import TextResponse

from kingfisher_scrapy.base_spiders.base_spider import BaseSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.items import File
from tests import spider_with_crawler


@pytest.mark.parametrize('sample,expected', [
    ('3', 3),
    ('true', 1),
    ('false', None),
    (None, None),
])
def test_sample(sample, expected):
    spider = spider_with_crawler(sample=sample)

    assert spider.sample == expected


def test_sample_no_kwarg():
    spider = BaseSpider(name='test')

    assert spider.sample is None


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

    actual = spider.build_file_from_response(response, file_name='file.json', data_type='release_package')

    assert actual == File({
        'file_name': 'file.json',
        'data': b'{"key": "value"}',
        "data_type": 'release_package',
        "url": 'https://example.com/remote.json',
    })


def test_build_file():
    spider = BaseSpider(name='test')

    data = b'{"key": "value"}'
    url = 'https://example.com/remote.json'

    actual = spider.build_file(file_name='file.json', url=url, data=data, data_type='release_package')

    assert actual == File({
        'file_name': 'file.json',
        'data': b'{"key": "value"}',
        "data_type": 'release_package',
        "url": 'https://example.com/remote.json',
    })


def test_sample_invalid():
    with pytest.raises(SpiderArgumentError) as e:
        spider_with_crawler(sample='invalid')
    assert str(e.value) == "spider argument `sample`: invalid integer value: 'invalid'"


def test_from_date():
    # No SpiderArgumentError exception.
    spider_with_crawler(from_date='2000-01-01')


def test_from_date_invalid():
    expected = "spider argument `from_date`: invalid date value: time data 'invalid' does not match format '%Y-%m-%d'"

    with pytest.raises(SpiderArgumentError) as e:
        spider_with_crawler(from_date='invalid')
    assert str(e.value) == expected


def test_until_date():
    # No SpiderArgumentError exception.
    spider_with_crawler(until_date='2000-01-01', default_from_date='2000-01-01')


def test_until_date_invalid():
    expected = "spider argument `until_date`: invalid date value: time data 'invalid' does not match format '%Y-%m-%d'"

    with pytest.raises(SpiderArgumentError) as e:
        spider_with_crawler(until_date='invalid', default_from_date='2000-01-01')
    assert str(e.value) == expected


def test_crawl_time():
    # No SpiderArgumentError exception.
    spider_with_crawler(crawl_time='2020-01-01T00:00:00')


def test_crawl_time_invalid():
    expected = "spider argument `crawl_time`: invalid date value: time data '2020' does not match format " \
               "'%Y-%m-%dT%H:%M:%S'"

    with pytest.raises(SpiderArgumentError) as e:
        spider_with_crawler(crawl_time='2020')
    assert str(e.value) == expected


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


def test_data_base_url_without_crawl_time():
    expected = "spider argument `crawl_time`: can't be blank if `DATABASE_URL` is set"

    with pytest.raises(SpiderArgumentError) as e:
        spider_with_crawler(settings={'DATABASE_URL': 'test'})
    assert str(e.value) == expected


def test_data_base_url_with_compile():
    # No SpiderArgumentError exception.
    spider_with_crawler(settings={'DATABASE_URL': 'test'}, crawl_time='2021-05-25T00:00:00', compile_releases='true')


@pytest.mark.parametrize('base_url,kwargs,expected', [
    # Empty `path` argument.
    ('http://example.com/a', {'path': ''}, 'http://example.com/a'),
    # `path` argument with trailing slash.
    ('http://example.com', {'path': 'a/'}, 'http://example.com/a/'),
    # `path` argument with unsafe characters.
    ('http://example.com', {'path': 'a?'}, 'http://example.com/a%3F'),
    # URL with trailing slash and without trailing slash.
    ('http://example.com/a', {'path': 'b/c'}, 'http://example.com/a/b/c'),
    ('http://example.com/a/', {'path': 'b/c'}, 'http://example.com/a/b/c'),
    # URL with query string and fragment identifier.
    ('http://example.com/a?k=v#frag', {'path': 'b/c'}, 'http://example.com/a/b/c'),
    # `path` argument with `qs` argument.
    ('http://example.com/a?k=v#frag', {'path': 'b/c', 'qs:param1': 'val1'}, 'http://example.com/a/b/c?param1=val1'),
])
def test_path_parameters(base_url, kwargs, expected):
    test_spider = type('TestSpider', (BaseSpider,), {
        'start_requests': lambda _self: [scrapy.Request(base_url)]
    })
    spider = spider_with_crawler(test_spider, **kwargs)

    for request in spider.start_requests():
        assert expected == request.url
