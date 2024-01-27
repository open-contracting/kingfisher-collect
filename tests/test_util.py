from datetime import datetime
from unittest.mock import Mock

import pytest
import scrapy

from kingfisher_scrapy.util import (
    components,
    date_range_by_interval,
    get_parameter_value,
    handle_http_error,
    join,
    parameters,
    replace_parameters,
)
from tests import spider_with_crawler


def parse_date(string):
    return datetime.strptime(string, '%Y-%m-%d').date()


@pytest.mark.parametrize('url,value,expected', [
    ('http://example.com/?page=1', 2, 'http://example.com/?page=2'),
    ('http://example.com/?page=1', None, 'http://example.com/'),
    ('http://example.com/', None, 'http://example.com/'),
])
def test_replace_parameters(url, value, expected):
    assert replace_parameters(url, page=value) == expected


@pytest.mark.parametrize('url,expected', [
    ('http://example.com/?page=1', '1'),
    ('http://example.com/?page=1&page=2', '1'),
    ('http://example.com/?page=', None),
    ('http://example.com/?page', None),
])
def test_get_parameter_value(url, expected):
    assert get_parameter_value(url, 'page') == expected


@pytest.mark.parametrize('url,extension,expected', [
    ('http://example.com/api/planning.json?page=1', None, 'planning-page-1'),
    ('http://example.com/api/planning?page=1', 'zip', 'planning-page-1.zip'),
])
def test_join(url, extension, expected):
    assert join(components(-1), parameters('page'), extension=extension)(url) == expected


@pytest.mark.parametrize('attempts', [0, 1])
def test_handle_http_error_retry(attempts):
    @handle_http_error
    def test_decorated(self, response, **kwargs):
        yield response

    spider = spider_with_crawler()
    spider.max_attempts = 3
    spider.retry_http_codes = [429]

    mock_response = Mock()
    mock_response.status = 429
    mock_response.headers = {'Retry-After': 5}
    meta = {}
    if attempts:
        meta['retries'] = attempts
    mock_response.request = scrapy.Request('http://test.com', meta=meta)

    actual = next(test_decorated(spider, mock_response))

    assert isinstance(actual, scrapy.Request)
    assert actual.meta['retries'] == attempts + 1
    assert actual.meta['wait_time'] == 5
    assert actual.dont_filter is True


def test_handle_http_error_max_attempts_reached():
    @handle_http_error
    def test_decorated(self, response, **kwargs):
        yield response

    spider = spider_with_crawler()
    spider.max_attempts = 3
    spider.retry_http_codes = [429]

    mock_response = Mock()
    mock_response.status = 429
    mock_response.headers = {'Retry-After': 5}
    mock_response.request = scrapy.Request('http://test.com', meta={'retries': 2})

    assert next(test_decorated(spider, mock_response)) == spider.build_file_error_from_response(mock_response)


@pytest.mark.parametrize('response_status', [200, 204])
def test_handle_http_error_success(response_status):
    @handle_http_error
    def test_decorated(self, response, **kwargs):
        yield response

    spider = spider_with_crawler()
    spider.max_attempts = 3
    spider.retry_http_codes = [429]

    mock_response = Mock()
    mock_response.status = response_status
    mock_response.request = scrapy.Request('http://test.com')

    assert next(test_decorated(spider, mock_response)) == mock_response


@pytest.mark.parametrize('response_status', [302, 400, 500])
def test_handle_http_error_error(response_status):
    @handle_http_error
    def test_decorated(self, response, **kwargs):
        yield response

    spider = spider_with_crawler()
    spider.max_attempts = 3
    spider.retry_http_codes = [429]

    mock_response = Mock()
    mock_response.status = response_status
    mock_response.request = scrapy.Request('http://test.com')

    assert next(test_decorated(spider, mock_response)) == spider.build_file_error_from_response(mock_response)


@pytest.mark.parametrize('start,stop,step,expected', [
    ('2022-01-01', '2022-01-01', 15, []),
    ('2022-01-01', '2022-01-25', 15, [('2022-01-10', '2022-01-25'), ('2022-01-01', '2022-01-10')]),
    ('2022-01-01', '2022-01-31', 15, [('2022-01-16', '2022-01-31'), ('2022-01-01', '2022-01-16')]),
    ('2022-01-01', '2022-01-03', 1, [('2022-01-02', '2022-01-03'), ('2022-01-01', '2022-01-02')]),
])
def test_date_range_by_interval(start, stop, step, expected):
    assert list(date_range_by_interval(parse_date(start), parse_date(stop), step)) == [
        tuple(parse_date(date) for date in dates) for dates in expected
    ]
