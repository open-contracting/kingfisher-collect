# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import datetime
import logging

from scrapy.exceptions import IgnoreRequest
from twisted.internet.defer import Deferred

logger = logging.getLogger(__name__)


class BaseDownloaderMiddleware:
    """Base class for downloader middlewares that need access to the spider instance."""

    def __init__(self, crawler):
        self.spider = crawler.spider
        self.engine = crawler.engine

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)


class ParaguayAuthMiddleware(BaseDownloaderMiddleware):
    """
    Downloader middleware that manages API authentication for Paraguay scrapers.

    Both DNCP (procurement authority) and Hacienda (finance ministry) use an authentication protocol based on OAuth 2.

    This middleware helps us to manage the protocol, which consists on acquiring an access token every x minutes
    (usually 15) and sending the token on each request. The acquisition method of the token is delegated to the spider,
    since each publisher has their own credentials and requirements.

    Apparently, a Downloader Middleware is the best place to set HTTP Request Headers (see
    https://docs.scrapy.org/en/latest/topics/architecture.html), but it's not enough for this case :(.
    Tokens should be generated and assigned just before sending a request, but Scrapy does not provide any way to do
    this, which in turn means that sometimes we accidentally send expired tokens. For now, the issue seems to be
    avoided by setting the number of concurrent requests to 1, at cost of download speed.

    .. code-block:: python

        class Paraguay:
            name = 'paraguay'

            # ParaguayAuthMiddleware
            access_token = None
            access_token_scheduled_at = None
            # The maximum age is less than the API's limit, since we don't precisely control Scrapy's scheduler.
            access_token_maximum_age = 14 * 60
            access_token_request_failed = False
            requests_backlog = []

            def build_access_token_request(self):
                self.access_token_scheduled_at = datetime.datetime.now()

                return scrapy.Request("https://example.com")
    """

    def process_request(self, request):
        if request.meta.get("auth") is False:
            return None
        if self.spider.access_token_request_failed:
            self.engine.close_spider_async(reason="access_token_request_failed")
            raise IgnoreRequest("Max attempts to get an access token reached. Stopping crawl...")
        request.headers["Authorization"] = self.spider.access_token
        if self._expires_soon():
            return self._add_request_to_backlog_and_build_access_token_request(request)
        return None

    def process_response(self, request, response):
        if response.status in {401, 429}:
            age = (datetime.datetime.now() - self.spider.access_token_scheduled_at).total_seconds()
            logger.info("Access token age: %ss", age)
            logger.info("%s returned for request to %s", response.status, request.url)
            if self.spider.access_token != request.headers["Authorization"] and self._expires_soon():
                return self._add_request_to_backlog_and_build_access_token_request(request)
            request.headers["Authorization"] = self.spider.access_token
            return request
        return response

    def _add_request_to_backlog_and_build_access_token_request(self, request):
        self.spider.requests_backlog.append(request)
        logger.info("Added request to backlog until token received: %s", request.url)
        return self.spider.build_access_token_request()

    def _expires_soon(self):
        if self.spider.access_token and self.spider.access_token_scheduled_at:
            age = (datetime.datetime.now() - self.spider.access_token_scheduled_at).total_seconds()
            if age < self.spider.access_token_maximum_age:
                return False
            logger.info("Access token age: %ss", age)
        return True


class OpenOppsAuthMiddleware(BaseDownloaderMiddleware):
    """Downloader middleware that intercepts requests and adds the token for OpenOpps scraper."""

    def process_request(self, request):
        if request.meta.get("token_request"):
            return
        request.headers["Authorization"] = self.spider.access_token


# https://github.com/ArturGaspar/scrapy-delayed-requests/blob/master/scrapy_delayed_requests.py
class DelayedRequestMiddleware:
    """
    Downloader middleware that allows for delaying a request by a set 'wait_time' number of seconds.

    A delayed request is useful when an API fails and works again after waiting a few minutes.
    """

    def process_request(self, request):
        delay = request.meta.get("wait_time", None)
        if delay:
            # https://docs.scrapy.org/en/latest/topics/asyncio.html#handling-a-pre-installed-reactor
            from twisted.internet import reactor  # noqa: PLC0415

            # Simulate a sleep.
            d = Deferred()
            reactor.callLater(delay, d.callback, None)
            return d
        return None
