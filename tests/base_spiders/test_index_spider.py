import re
from math import ceil

import pytest
from scrapy import Request
from scrapy.http import TextResponse

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.util import parameters
from tests import spider_with_crawler

TEST_CASES = [
    # honduras_portal_*
    (
        {
            "data_type": "release_package",
            "page_count_pointer": "/results",
            "formatter": staticmethod(parameters("page")),
        },
        '{"results": 10}',
        "http://example.com",
        r"http://example\.com\?page=(\d+)",
        [str(x) for x in range(2, 11)],
    ),
    (
        {
            "data_type": "release_package",
            "page_count_pointer": "/results",
            "formatter": staticmethod(parameters("page")),
        },
        '{"results": 10}',
        "http://example.com?pageSize=10",
        r"http://example\.com\?pageSize=10&page=(\d+)",
        [str(x) for x in range(2, 11)],
    ),
    # mexico_administracion_publica_federal
    (
        {
            "data_type": "release_package",
            "result_count_pointer": "/total",
            "limit": "/limit",
            "use_page": True,
            "formatter": staticmethod(parameters("page")),
        },
        '{"total": 50, "limit": 10}',
        "http://example.com",
        r"http://example\.com\?page=(\d+)",
        [str(x) for x in range(2, 6)],
    ),
    # canada_montreal
    (
        {
            "data_type": "release_package",
            "result_count_pointer": "/total",
            "limit": 10,
            "formatter": staticmethod(parameters("offset")),
        },
        '{"total": 50}',
        "http://example.com",
        r"http://example\.com\?limit=10&offset=(\d+)",
        [str(x) for x in range(10, 50, 10)],
    ),
    # canada_montreal, but with a JSON Pointer for limit
    (
        {
            "data_type": "release_package",
            "result_count_pointer": "/total",
            "limit": "/limit",
            "formatter": staticmethod(parameters("offset")),
        },
        '{"total": 50, "limit": 10}',
        "http://example.com",
        r"http://example\.com\?limit=10&offset=(\d+)",
        [str(x) for x in range(10, 50, 10)],
    ),
    # kenya_makueni
    (
        {
            "data_type": "release_package",
            "formatter": staticmethod(parameters("pageNumber")),
            "param_page": "pageNumber",
            "base_url": "http://example.com/ocds?step=10",
            "range_generator": lambda _self, _data, response: range(ceil(int(response.text) / 10)),
            "url_builder": lambda _self, value, data, response: _self.pages_url_builder(value, data, response),
        },
        "100",
        "http://example.com",
        r"http://example\.com/ocds\?step=10&pageNumber=(\d+)",
        [str(x) for x in range(10)],
    ),
]


@pytest.mark.parametrize(
    ("spider_args", "start_request_response", "initial_url", "results_pattern", "expected"), TEST_CASES
)
def test_urls(spider_args, start_request_response, initial_url, results_pattern, expected):
    text_response_mock = TextResponse(
        initial_url,
        status=200,
        headers={"Content-type": "text/html"},
        encoding="utf-8",
        body=start_request_response,
        request=Request(url=initial_url, meta={"file_name": "list.json"}),
    )

    test_spider = type("TestSpider", (IndexSpider,), {"name": "test"} | spider_args)

    spider = spider_with_crawler(spider_class=test_spider)

    requests = list(spider.parse_list(text_response_mock))

    if "base_url" in spider_args:
        assert len(requests) == len(expected)
        range_to_evaluate = requests
    else:
        assert len(requests) == len(expected) + 1
        range_to_evaluate = requests[1:]

    regexp = re.compile(results_pattern)
    for request, expected_param in zip(range_to_evaluate, expected, strict=False):
        match = regexp.match(request.url)
        assert match is not None, f"{request.url!r} !~ {regexp!r}"
        assert match.group(1) == expected_param
