import asyncio
import time

from scrapy import Request
from scrapy.core.downloader import DownloaderMiddlewareManager
from scrapy.utils.reactor import install_reactor

from tests import spider_with_crawler

install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")


# Running this as a pytest test raises "twisted.internet.error.ReactorAlreadyRunning".
def delayed_request_middleware():
    async def download_func(request):
        return request

    spider = spider_with_crawler(
        settings={
            "DOWNLOADER_MIDDLEWARES": {
                "scrapy.downloadermiddlewares.offsite.OffsiteMiddleware": None,
                "kingfisher_scrapy.downloadermiddlewares.DelayedRequestMiddleware": 543,
            },
        }
    )
    request = Request("http://example.com", meta={"wait_time": 1})
    # The request is sent to all the downloader middlewares, including the delayed request middleware.
    manager = DownloaderMiddlewareManager.from_crawler(spider.crawler)

    start = time.time()
    result = asyncio.get_event_loop().run_until_complete(manager.download_async(download_func, request))
    spent = time.time() - start

    assert result == request, result
    assert 1 <= spent <= 1.5, spent


if __name__ == "__main__":
    delayed_request_middleware()
