import pytest

from kingfisher_scrapy.util import get_parameter_value, replace_parameter


@pytest.mark.parametrize('url,value,expected', [
    ('http://example.com/?page=1', 2, 'http://example.com/?page=2'),
    ('http://example.com/?page=1', None, 'http://example.com/'),
    ('http://example.com/', None, 'http://example.com/'),
])
def test_replace_parameter(url, value, expected):
    assert replace_parameter(url, 'page', value) == expected


@pytest.mark.parametrize('url,parameter_name,expected', [
    ('http://example.com/?page=1', 'page', 1),
    ('http://example.com/?page=1', None, 1),
    ('http://example.com/?page', None, None),
])
def test_get_parameter_value(url, parameter_name, expected):
    assert get_parameter_value(url, 'page') == expected
