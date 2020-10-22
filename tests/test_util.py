import pytest

from kingfisher_scrapy.util import components, get_parameter_value, replace_parameters


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


@pytest.mark.parametrize('url,expected', [
    ('http://example.com/example/file.json', 'file'),
    ('http://example.com/example/file.xlsx', 'file'),
    ('http://example.com/example/file.csv', 'file'),
])
def test_components(url, expected):
    assert components(-1)(url) == expected
