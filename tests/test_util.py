import pytest

from kingfisher_scrapy.util import replace_parameter


@pytest.mark.parametrize('url,value,expected', [
    ('http://example.com/?page=1', 2, 'http://example.com/?page=2'),
    ('http://example.com/?page=1', None, 'http://example.com/'),
    ('http://example.com/', None, 'http://example.com/'),
])
def test_replace_parameter(url, value, expected):
    assert replace_parameter(url, 'page', value) == expected
