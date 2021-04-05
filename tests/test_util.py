from datetime import datetime

import pytest

from kingfisher_scrapy.util import components, get_parameter_value, join, parameters, replace_parameters


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
