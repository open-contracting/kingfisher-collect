# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from datetime import datetime

from scrapy.exceptions import IgnoreRequest
from twisted.internet.defer import Deferred


class ParaguayAuthMiddleware:
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
                self.access_token_scheduled_at = datetime.now()

                return scrapy.Request("https://example.com")
    """

    def __init__(self, spider):
        spider.logger.info('Initialized authentication middleware with spider: %s.', spider.name)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider)

    def process_request(self, request, spider):
        if 'auth' in request.meta and request.meta['auth'] is False:
            return
        if spider.access_token_request_failed:
            spider.crawler.engine.close_spider(spider, 'access_token_request_failed')
            raise IgnoreRequest("Max attempts to get an access token reached. Stopping crawl...")
        request.headers['Authorization'] = spider.access_token
        if self._expires_soon(spider):
            return self.add_request_to_backlog_and_build_access_token_request(spider, request)

    def process_response(self, request, response, spider):
        if response.status == 401 or response.status == 429:
            age = (datetime.now() - spider.access_token_scheduled_at).total_seconds()
            spider.logger.info('Access token age: %ss', age)
            spider.logger.info('%s returned for request to %s', response.status, request.url)
            if not spider.access_token == request.headers['Authorization'] and self._expires_soon(spider):
                return self.add_request_to_backlog_and_build_access_token_request(spider, request)
            request.headers['Authorization'] = spider.access_token
            return request
        return response

    def add_request_to_backlog_and_build_access_token_request(self, spider, request):
        spider.requests_backlog.append(request)
        spider.logger.info('Added request to backlog until token received: %s', request.url)
        return spider.build_access_token_request()

    @staticmethod
    def _expires_soon(spider):
        if spider.access_token and spider.access_token_scheduled_at:
            age = (datetime.now() - spider.access_token_scheduled_at).total_seconds()
            if age < spider.access_token_maximum_age:
                return False
            spider.logger.info('Access token age: %ss', age)
        return True


class OpenOppsAuthMiddleware:
    """
    Downloader middleware that intercepts requests and adds the token for OpenOpps scraper.
    """

    @staticmethod
    def process_request(request, spider):
        if 'token_request' in request.meta and request.meta['token_request']:
            return
        request.headers['Authorization'] = spider.access_token


# https://github.com/ArturGaspar/scrapy-delayed-requests/blob/master/scrapy_delayed_requests.py
class DelayedRequestMiddleware:
    """
    Downloader middleware that allows for delaying a request by a set 'wait_time' number of seconds.

    A delayed request is useful when an API fails and works again after waiting a few minutes.
    """

    def process_request(self, request, spider):
        delay = request.meta.get('wait_time', None)
        if delay:
            from twisted.internet import reactor

            d = Deferred()
            reactor.callLater(delay, d.callback, None)
            return d
