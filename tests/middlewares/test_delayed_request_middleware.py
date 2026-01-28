import pytest
from scrapy import Request
from twisted.internet.defer import Deferred

from kingfisher_scrapy.downloadermiddlewares import DelayedRequestMiddleware


@pytest.mark.parametrize(
    ("meta", "expected"),
    [
        (None, type(None)),
        ({"wait_time": 1}, Deferred),
    ],
)
def test_middleware_output(meta, expected):
    middleware = DelayedRequestMiddleware()
    request = Request("http://example.com", meta=meta)
    output = middleware.process_request(request)

    assert isinstance(output, expected)
