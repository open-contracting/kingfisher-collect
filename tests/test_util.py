from datetime import datetime

import pytest

from kingfisher_scrapy.util import components, get_parameter_value, join, parameters, replace_parameters, date_range


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


def test_date_range():
    start = datetime.strptime('2020-01-01', '%Y-%m-%d')
    stop = datetime.strptime('2020-01-15', '%Y-%m-%d')
    dates = list(date_range(start, stop))
    assert len(dates) == 15
    assert dates[0] == '2020-01-15'
    assert dates[-1] == '2020-01-01'
