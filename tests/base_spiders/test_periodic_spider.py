import datetime

import pytest

from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import components, date_range_by_interval, date_range_by_month, date_range_by_year
from tests import spider_with_crawler

today = datetime.datetime.now(tz=datetime.timezone.utc).date()
today_year_month = today.strftime("%Y-%m")
today_date = today.strftime("%Y-%m-%d")
pattern_year = "http://example.com/{}"
pattern_year_month = "http://example.com/{0:%Y-%m}"
pattern_date = "http://example.com/{0:%Y-%m-%d}/{1:%Y-%m-%d}"


def _format_urls(arg_type, pattern, arg_start, arg_end):
    if arg_type == "year":
        date_range = date_range_by_year
        start = arg_start.year
        end = arg_end.year
    elif arg_type == "year-month":
        date_range = date_range_by_month
        start = arg_start
        end = arg_end
    else:
        return [pattern.format(x, y) for x, y in date_range_by_interval(arg_start, arg_end, 1)]

    return [pattern.format(x) for x in date_range(start, end)]


TEST_CASES = {
    # default from date
    "default_from-year": (
        "year",
        pattern_year,
        "2011",
        today.year,
        {
            "default_from_date": "2011",
        },
        {},
    ),
    "default_from-year_month": (
        "year-month",
        pattern_year_month,
        "2011-06",
        today_year_month,
        {
            "default_from_date": "2011-06",
        },
        {},
    ),
    "default_from-date": (
        "date",
        pattern_date,
        "2011-06-15",
        today_date,
        {
            "default_from_date": "2011-06-15",
        },
        {},
    ),
    # default from and until dates, in each date format
    "default_from_until-year": (
        "year",
        pattern_year,
        "2011",
        "2019",
        {
            "default_from_date": "2011",
            "default_until_date": "2019",
        },
        {},
    ),
    "default_from_until-year_month": (
        "year-month",
        pattern_year_month,
        "2011-06",
        "2019-12",
        {
            "default_from_date": "2011-06",
            "default_until_date": "2019-12",
        },
        {},
    ),
    "default_from_until-date": (
        "date",
        pattern_date,
        "2011-06-15",
        "2019-12-31",
        {
            "default_from_date": "2011-06-15",
            "default_until_date": "2019-12-31",
        },
        {},
    ),
    # user-specified from_date, in each date format
    "user_from-year": (
        "year",
        pattern_year,
        "2017",
        today.year,
        {
            "default_from_date": "2011",
        },
        {
            "from_date": "2017",
        },
    ),
    "user_from-year_month": (
        "year-month",
        pattern_year_month,
        "2017-06",
        today_year_month,
        {
            "default_from_date": "2011-01",
        },
        {
            "from_date": "2017-06",
        },
    ),
    "user_from-date": (
        "date",
        pattern_date,
        "2017-06-15",
        today_date,
        {
            "default_from_date": "2011-01-01",
        },
        {
            "from_date": "2017-06-15",
        },
    ),
    # user-specific until_date, in each date format
    "user_until-year": (
        "year",
        pattern_year,
        "2011",
        "2017",
        {
            "default_from_date": "2011",
            "default_until_date": "2019",
        },
        {
            "until_date": "2017",
        },
    ),
    "user_until-year_month": (
        "year-month",
        pattern_year_month,
        "2011-01",
        "2017-06",
        {
            "default_from_date": "2011-01",
            "default_until_date": "2019-12",
        },
        {
            "until_date": "2017-06",
        },
    ),
    "user_until-date": (
        "date",
        pattern_date,
        "2011-01-01",
        "2017-06-15",
        {
            "default_from_date": "2011-01-01",
            "default_until_date": "2019-12-31",
        },
        {
            "until_date": "2017-06-15",
        },
    ),
    # user-specified sample parameter
    "user_sample-year": (
        "year",
        "http://example.com/{}",
        today.year,
        today.year,
        {
            "default_from_date": "2011",
        },
        {
            "sample": "true",
        },
    ),
    "user_sample-year_month": (
        "year-month",
        "http://example.com/{}",
        today_year_month,
        today_year_month,
        {
            "default_from_date": "2011-06",
        },
        {
            "sample": "true",
        },
    ),
    "user_sample-date": (
        "date",
        "http://example.com/{}/{}",
        today_date,
        today_date,
        {
            "default_from_date": "2011-06-15",
        },
        {
            "sample": "true",
        },
    ),
}


@pytest.mark.parametrize(
    ("date_format", "pattern", "expected_start", "expected_end", "class_args", "user_args"),
    TEST_CASES.values(),
    ids=TEST_CASES.keys(),
)
def test_urls(date_format, pattern, expected_start, expected_end, class_args, user_args):
    expected = _format_urls(
        date_format,
        pattern,
        datetime.datetime.strptime(str(expected_start), PeriodicSpider.VALID_DATE_FORMATS[date_format]),
        datetime.datetime.strptime(str(expected_end), PeriodicSpider.VALID_DATE_FORMATS[date_format]),
    )

    test_spider = type(
        "TestSpider",
        (PeriodicSpider,),
        {
            "name": "test",
            "date_format": date_format,
            "formatter": staticmethod(components(-1)),
            "pattern": pattern,
        }
        | class_args,
    )
    spider = spider_with_crawler(spider_class=test_spider, **user_args)

    requests = list(spider.start_requests())

    for request, expected_url in zip(requests, expected, strict=False):
        assert request.url == expected_url
