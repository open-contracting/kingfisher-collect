from unittest.mock import Mock

import pytest
import scrapy

from kingfisher_scrapy.util import (components, get_parameter_value, handle_http_error, join, parameters,
                                    replace_parameters)
from tests import spider_with_crawler


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


@pytest.mark.parametrize('response_status,retry_http_codes,retry_after,attempt', [
    (200, [], None, 0),
    (404, [], None, 0),
    (429, [429], 5, 0),
    (429, [429], 5, 2),
])
def test_handle_http_error(response_status, retry_http_codes, retry_after, attempt):
    @handle_http_error
    def test_decorated(self, response, **kwargs):
        return [response]

    spider = spider_with_crawler()
    spider.retry_http_codes = retry_http_codes
    mock_response = Mock()
    mock_response.status = response_status
    mock_response.headers = {'Retry-After': retry_after}
    mock_response.request = scrapy.Request('http://test.com', meta={'retries': attempt})
    # Test no errors
    if response_status == 200:
        assert next(test_decorated(spider, mock_response)) == mock_response
    # Test regular non handle errors
    elif not retry_http_codes:
        assert next(test_decorated(spider, mock_response)) == spider.build_file_error_from_response(mock_response)
    # Test first retry attempt
    elif attempt == 0:
        spider.max_attempts = 2
        request_to_retry = next(test_decorated(spider, mock_response))
        mock_response.request.meta['retries'] = attempt + 1
        mock_response.request.meta['wait_time'] = retry_after
        assert request_to_retry.meta == mock_response.request.meta
    # Test too many attempts
    else:
        assert next(test_decorated(spider, mock_response)) == spider.build_file_error_from_response(mock_response)
