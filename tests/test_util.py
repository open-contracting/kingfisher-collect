from datetime import datetime

import pytest

from kingfisher_scrapy.util import (
    components,
    date_range_by_interval,
    get_parameter_value,
    join,
    parameters,
    replace_parameters,
)


def parse_date(string):
    return datetime.strptime(string, "%Y-%m-%d").date()


@pytest.mark.parametrize(
    ("url", "value", "expected"),
    [
        ("http://example.com/?page=1", 2, "http://example.com/?page=2"),
        ("http://example.com/?page=1", None, "http://example.com/"),
        ("http://example.com/", None, "http://example.com/"),
    ],
)
def test_replace_parameters(url, value, expected):
    assert replace_parameters(url, page=value) == expected


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("http://example.com/?page=1", "1"),
        ("http://example.com/?page=1&page=2", "1"),
        ("http://example.com/?page=", None),
        ("http://example.com/?page", None),
    ],
)
def test_get_parameter_value(url, expected):
    assert get_parameter_value(url, "page") == expected


@pytest.mark.parametrize(
    ("url", "extension", "expected"),
    [
        ("http://example.com/api/planning.json?page=1", None, "planning-page-1"),
        ("http://example.com/api/planning?page=1", "zip", "planning-page-1.zip"),
    ],
)
def test_join(url, extension, expected):
    assert join(components(-1), parameters("page"), extension=extension)(url) == expected


@pytest.mark.parametrize(
    ("start", "stop", "step", "expected"),
    [
        ("2022-01-01", "2022-01-01", 15, []),
        ("2022-01-01", "2022-01-25", 15, [("2022-01-10", "2022-01-25"), ("2022-01-01", "2022-01-10")]),
        ("2022-01-01", "2022-01-31", 15, [("2022-01-16", "2022-01-31"), ("2022-01-01", "2022-01-16")]),
    ],
)
def test_date_range_by_interval(start, stop, step, expected):
    assert list(date_range_by_interval(parse_date(start), parse_date(stop), step)) == [
        tuple(parse_date(date) for date in dates) for dates in expected
    ]


def test_date_range_by_interval_edge_case():
    assert list(date_range_by_interval(datetime(2001, 1, 1, 0, 0), datetime(2001, 1, 3, 0, 0), 1)) == [
        (datetime(2001, 1, 2, 0, 0), datetime(2001, 1, 3, 0, 0)),
        (datetime(2001, 1, 1, 0, 0), datetime(2001, 1, 2, 0, 0)),
    ]
