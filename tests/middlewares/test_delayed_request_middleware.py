import pytest
from scrapy import Request

from kingfisher_scrapy.downloadermiddlewares import DelayedRequestMiddleware


@pytest.mark.parametrize("meta", [None, {"wait_time": 0}])
async def test_middleware_output(meta):
    middleware = DelayedRequestMiddleware()
    request = Request("http://example.com", meta=meta)
    await middleware.process_request(request)
