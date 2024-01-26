from datetime import datetime

import pytest

from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import components, date_range_by_interval, date_range_by_month, date_range_by_year
from tests import spider_with_crawler


def _format_urls(arg_type, pattern, arg_start, arg_end):
    if arg_type == 'year':
        date_range = date_range_by_year
        start = arg_start.year
        end = arg_end.year
    elif arg_type == 'year-month':
        date_range = date_range_by_month
        start = arg_start
        end = arg_end
    else:
        return [pattern.format(x, y) for x, y in date_range_by_interval(arg_start, arg_end, 1)]

    return [pattern.format(x) for x in date_range(start, end)]


TEST_CASES = [
    # default from date
    ('year', 'http://example.com/{}', '2012', datetime.today().year, {'default_from_date': '2012'}, {}),
    ('year-month', 'http://example.com/{:%Y-%m}', '2010-06', datetime.today().strftime('%Y-%m'), {
        'default_from_date': '2010-06'
    }, {}),
    # default from & end dates
    ('year', 'http://example.com/{}', '2012', '2016', {
        'default_from_date': '2012',
        'default_until_date': '2016'
    }, {}),
    ('year-month', 'http://example.com/{:%Y-%m}', '2010-06', '2019-12', {
        'default_from_date': '2010-06',
        'default_until_date': '2019-12'
    }, {}),
    ('date', 'http://example.com/{:%Y-%m-%d}/{:%Y-%m-%d}', '2010-06-01', '2019-12-10', {
        'default_from_date': '2010-06-01',
        'default_until_date': '2019-12-10',
        'step': 1
    }, {}),
    # from_date specified by the user
    ('year', 'http://example.com/{}', '2017', datetime.today().year, {
        'default_from_date': '2008'
    }, {
        'from_date': '2017'
    }),
    ('year-month', 'http://example.com/{:%Y-%m}', '2018-01', datetime.today().strftime('%Y-%m'), {
        'default_from_date': '2011-01'
    }, {
        'from_date': '2018-01'
    }),
    # until_date specified by the user
    ('year', 'http://example.com/{}', '2008', '2010', {
        'default_from_date': '2008',
        'default_until_date': '2017'
    }, {
        'until_date': '2010'
    }),
    ('year-month', 'http://example.com/{:%Y-%m}', '2011-01', '2019-06', {
        'default_from_date': '2011-01'
    }, {
        'until_date': '2019-06'
    }),
    ('date', 'http://example.com/{0:%Y-%m-%d}/{1:%Y-%m-%d}', '2011-01-01', '2019-06-01', {
        'default_from_date': '2011-01-01', 'step': 1
    }, {
        'until_date': '2019-06-01'
     }),
    # pass the 'sample' parameter
    ('year', 'http://example.com/{}', datetime.today().year, datetime.today().year, {
        'default_from_date': '2008',
    }, {
        'sample': 'true'
    }),
]


@pytest.mark.parametrize(
    'date_format,pattern,expected_start,expected_end,class_args,user_args',
    TEST_CASES)
def test_urls(date_format, pattern, expected_start, expected_end, class_args, user_args):
    expected = _format_urls(
        date_format,
        pattern,
        datetime.strptime(str(expected_start), PeriodicSpider.VALID_DATE_FORMATS[date_format]),
        datetime.strptime(str(expected_end), PeriodicSpider.VALID_DATE_FORMATS[date_format])
    )

    test_spider = type(
        'TestSpider',
        (PeriodicSpider,),
        dict(date_format=date_format, formatter=staticmethod(components(-1)), pattern=pattern, **class_args),
    )
    spider = spider_with_crawler(spider_class=test_spider, **user_args)

    requests = list(spider.start_requests())

    for request, expected_url in zip(requests, expected):
        assert request.url == expected_url
