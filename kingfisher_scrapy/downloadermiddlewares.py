# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import asyncio
import datetime
import logging
import socket

import scrapy.http
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.defer import deferred_from_coro

from kingfisher_scrapy.responses import JSONResponse
from kingfisher_scrapy.util import post_slack_alert

logger = logging.getLogger(__name__)


class BaseDownloaderMiddleware:
    """Base class for downloader middlewares that need access to the spider instance."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.spider = crawler.spider

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
            # See scrapyextensions/closespider.py and the docstring for scrapy.utils.defer._schedule_coro().
            deferred_from_coro(self.crawler.engine.close_spider_async(reason="access_token_request_failed"))
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


class DelayedRequestMiddleware:
    """
    Downloader middleware that allows for delaying a request by a set 'wait_time' number of seconds.

    A delayed request is useful when an API fails and works again after waiting a few minutes.
    """

    async def process_request(self, request):
        delay = request.meta.get("wait_time", None)
        if delay:
            await asyncio.sleep(delay)


class CloudflareMiddleware(BaseDownloaderMiddleware):
    """
    Downloader middleware that reuses a manually-solved Cloudflare Turnstile clearance and detects when it is stale.

    It is active only for spiders that set ``cloudflare_protected = True``, so it is safe to enable globally.

    A human separately solves the "Verify you are human" check, and the spider reuses the resulting ``cf_clearance``
    cookie (the ``CF_CLEARANCE`` setting). Cloudflare binds the cookie to the browser, operating system and IP that
    solved the check, and verifies all three on every later request. So, the check must be solved using the same
    browser, operating system and IP as future crawls:

    -  The browser and operating system are *impersonated* using the ``CF_USER_AGENT`` (User-Agent header) and
       ``CURL_IMPERSONATE`` (TLS/JA3 fingerprint) settings.
    -  The IP can *not* be impersonated, so the check must be solved using the same IP as future crawls, and using the
       same IP version (the ``CURL_IP_VERSION`` setting).

    An HTML content type is treated as a Cloudflare challenge. If so, the middleware posts a Slack message (to the
    ``SLACK_WEBHOOK_URL`` setting) and stops the crawl.

    .. seealso:: :class:`~kingfisher_scrapy.downloadhandlers.CurlImpersonateDownloadHandler`
    """

    def __init__(self, crawler):
        super().__init__(crawler)
        self.cf_clearance = crawler.settings.get("CF_CLEARANCE")
        self.slack_webhook_url = crawler.settings.get("SLACK_WEBHOOK_URL")

    def process_request(self, request):
        if not self.spider.cloudflare_protected or not self.cf_clearance:
            return

        # Cookies are disabled globally (the COOKIES_ENABLED setting), so set the Cookie header directly.
        cookie = f"cf_clearance={self.cf_clearance}"
        if existing := request.headers.get("Cookie"):
            cookie = f"{existing.decode()}; {cookie}"
        request.headers["Cookie"] = cookie

    def process_response(self, request, response):
        if not self.spider.cloudflare_protected or b"text/html" not in response.headers.get("Content-Type", b""):
            return response

        logger.error("Cloudflare challenge detected for %s. The CF_CLEARANCE cookie must be re-set.", request.url)
        post_slack_alert(
            self.slack_webhook_url,
            f"{self.spider.name}: Cloudflare returned a challenge for {request.url}. The CF_CLEARANCE cookie must "
            f"be re-set from the same browser, operating system and IP, on {socket.gethostname()}.",
        )

        # See scrapyextensions/closespider.py and the docstring for scrapy.utils.defer._schedule_coro().
        deferred_from_coro(self.crawler.engine.close_spider_async(reason="cf_clearance_stale"))
        raise IgnoreRequest(f"Cloudflare challenge detected for {request.url}. Stopping crawl...")


class OrjsonMiddleware:
    """Downloader middleware that replaces the response class for faster JSON parsing."""

    def process_response(self, request, response):
        if type(response) in (scrapy.http.TextResponse, scrapy.http.JsonResponse):
            return response.replace(cls=JSONResponse)
        return response
