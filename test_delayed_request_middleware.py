import time

from scrapy import Request
from scrapy.core.downloader import DownloaderMiddlewareManager
from twisted.internet.defer import Deferred
from twisted.trial.unittest import TestCase

from tests import spider_with_crawler


# Running this as a pytest test raises "twisted.internet.error.ReactorAlreadyRunning".
def delayed_request_middleware():

    def download_func(spider, request):
        return request

    spider = spider_with_crawler(settings={
        'DOWNLOADER_MIDDLEWARES': {
            'kingfisher_scrapy.downloadermiddlewares.DelayedRequestMiddleware': 543,
        },
    })
    request = Request('http://example.com', meta={'wait_time': 1})
    # We send the request to all the downloader middlewares, including the delayed request middleware.
    manager = DownloaderMiddlewareManager.from_crawler(spider.crawler)
    downloaded = manager.download(download_func, request, spider)

    assert isinstance(downloaded, Deferred)

    start = time.time()

    # https://github.com/scrapy/scrapy/blob/28262d4b241744aa7c090702db9a89411e3bbf9a/tests/test_downloadermiddleware.py#L36
    results = []
    downloaded.addBoth(results.append)
    test = TestCase()
    test._wait(downloaded)

    end = time.time()

    assert results == [request]
    assert 1 <= end - start <= 1.01


if __name__ == "__main__":
    delayed_request_middleware()
