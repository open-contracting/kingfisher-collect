import pytest
from scrapy import Request
from scrapy.core.downloader import DownloaderMiddlewareManager
from twisted.internet.defer import Deferred
from twisted.trial.unittest import TestCase

from kingfisher_scrapy.downloadermiddlewares import DelayedRequestMiddleware
from tests import spider_with_crawler


# pytest-asyncio causes "Event loop is closed".
@pytest.mark.order(1)
@pytest.mark.parametrize('meta,expected', [
    (None, type(None)),
    ({'wait_time': 1}, Deferred),
])
def test_middleware_output(meta, expected):
    spider = spider_with_crawler()
    middleware = DelayedRequestMiddleware()
    request = Request('http://example.com', meta=meta)
    output = middleware.process_request(request, spider)

    assert isinstance(output, expected)


def test_middleware_wait():

    def download_func(spider, request):
        return request

    spider = spider_with_crawler()
    request = Request('http://example.com', meta={'wait_time': 1})
    # We send the request to all the downloader middlewares, including the delayed request middleware.
    manager = DownloaderMiddlewareManager.from_crawler(spider.crawler)
    downloaded = manager.download(download_func, request, spider)

    assert isinstance(downloaded, Deferred)

    # https://github.com/scrapy/scrapy/blob/28262d4b241744aa7c090702db9a89411e3bbf9a/tests/test_downloadermiddleware.py#L36
    results = []
    downloaded.addBoth(results.append)
    test = TestCase()
    test._wait(downloaded)

    assert len(results) == 1
    assert results[0].url == request.url
