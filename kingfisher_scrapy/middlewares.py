# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from datetime import datetime

import scrapy
from twisted.internet import reactor
from twisted.internet.defer import Deferred

WAIT_META = 'wait_time'


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
    this, which in turn means that sometimes we accidently send expired tokens. For now, the issue seems to be avoided
    by setting the number of concurrent requests to 1, at cost of download speed.
    """

    def __init__(self, spider):
        spider.logger.info('Initialized authentication middleware with spider: %s.', spider.name)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider)

    def process_request(self, request, spider):
        if 'auth' in request.meta and request.meta['auth'] is False:
            return
        if spider.auth_failed:
            spider.logger.error('Fatal: no authentication token, stopping now...')
            spider.crawler.stop()
            raise scrapy.exceptions.IgnoreRequest()
        request.headers['Authorization'] = spider.access_token
        if self._expires_soon(spider):
            # SAVE the last request to continue after getting the token
            spider.last_request = request
            # spider MUST implement the request_access_token method
            return spider.request_access_token()

    def process_response(self, request, response, spider):
        if response.status == 401 or response.status == 429:
            spider.logger.info('Time transcurred: %s', (datetime.now() - spider.start_time).total_seconds())
            spider.logger.info('%s returned for request to %s', response.status, request.url)
            if not spider.access_token == request.headers['Authorization'] and self._expires_soon(spider):
                # SAVE the last request to continue after getting the token
                spider.last_request = request
                # spider MUST implement the request_access_token method
                return spider.request_access_token()
            request.headers['Authorization'] = spider.access_token
            return request
        return response

    @staticmethod
    def _expires_soon(spider):
        if spider.start_time and spider.access_token:
            # The spider must implement the expires_soon method.
            return spider.expires_soon(datetime.now() - spider.start_time)
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
class DelayedRequestsMiddleware:

    """
    Downloader middleware that allows for delaying a request by a set 'wait_time' number of seconds.

    A delayed request is useful when an API fails and works again after waiting a few minutes.
    """
    def process_request(self, request, spider):
        delay = request.meta.get(WAIT_META, None)
        if delay:
            d = Deferred()
            reactor.callLater(delay, d.callback, None)
            return d
