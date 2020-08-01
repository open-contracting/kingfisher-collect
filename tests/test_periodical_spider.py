import pytest
from datetime import date, datetime

from . import spider_with_crawler
from kingfisher_scrapy.base_spider import PeriodicalSpider
from kingfisher_scrapy.util import components, date_range_by_year, date_range_by_month


def _get_urls(type, pattern, arg_start, arg_end=datetime.now()):
    if type == 'year':
        date_range = date_range_by_year
        start = arg_start.year
        end = arg_end.year
    else:
        date_range = date_range_by_month
        start = datetime.strptime(arg_start, '%Y-%m')
        end = datetime.strptime(arg_end, '%Y-%m')

    return [pattern.format(x) for x in date_range(start, end)]


@pytest.mark.parametrize('date,date_format,expected', [
    (2008, 'year', '2008'),
    ('2007-10', 'year-month', '2007-10')
])
def test_default_from_date(date, date_format, expected):
    spider = PeriodicalSpider(name='test', start=date, date_format=date_format)
    assert spider.default_from_date == expected


@pytest.mark.parametrize('start,from_date,date_format,pattern,expected_start', [
    (2008, 2017, 'year', 'http://example.com/{}', 2017),
    ('2011-01', '2018-01', 'year-month', 'http://example.com/{%Y-%m}', '2018-01')
])
def test_start(start, from_date, date_format, pattern, expected_start):
    expected = _get_urls(date_format, pattern, datetime.strptime(str(expected_start), date_format))

    TestSpider = type('TestSpider', (PeriodicalSpider,), dict(start=start, date_format=date_format,
                                                              get_formatter=lambda x: components(-1), pattern=pattern))

    spider = spider_with_crawler(spider_class=TestSpider, from_date=str(from_date))

    requests = [x for x in spider.start_requests()]

    assert len(requests) == len(expected)
