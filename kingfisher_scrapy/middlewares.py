# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import scrapy
import logging
from datetime import datetime
from kingfisher_scrapy.exceptions import AuthenticationFailureException


class HttpProxyWithSpiderArgsMiddleware(object):

    def __init__(self, spider):
        logging.info('Using HttpProxyWithSpiderArgsMiddleware.')
        if not hasattr(spider, 'http_proxy') and not hasattr(spider, 'https_proxy'):
            logging.warning('No proxy arguments have been set!')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider)

    def process_request(self, request, spider):
        if request.url.startswith('https:') and hasattr(spider, 'https_proxy'):
            request.meta['proxy'] = spider.https_proxy
        elif request.url.startswith('http:') and hasattr(spider, 'http_proxy'):
            request.meta['proxy'] = spider.http_proxy


class ParaguayAuthMiddleware(object):
    """Downloader middleware that manages API authentication for Paraguay
    scrapers.

    Both DNCP (procurement authority) and Hacienda (finance ministry) use an
    authentication protocol based on OAuth 2.0.

    This middleware helps us to manage the protocol, which
    consists on acquiring an access token every x minutes (usually 15) and
    sending the token on each request. The acquisition method of the token is
    delegated to the spider, since each publisher has their own credentials and
    requirements.

    Apparently, a Downloader Middleware is the best place to set HTTP Request
    Headers (see https://docs.scrapy.org/en/latest/topics/architecture.html), but it's not enough for this case :(.
    Tokens should be generated and assigned just before sending a request,
    but Scrapy does not provide any way to do this, which in turn means that sometimes we accidently send expired tokens.
    For now, the issue seems to be avoided by setting the number of
    concurrent requests to 1, at cost of download speed.

    """

    def __init__(self, spider):
        logging.info('Initialized authentication middleware with spider: {}.'.format(spider.name))
        AuthManager.reset_access_token(spider)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider)

    def process_request(self, request, spider):
        if 'auth' in request.meta and request.meta['auth'] is not None and not request.meta['auth']:
            return
        if AuthManager.auth_failed:
            logging.error('Fatal: no authentication token, stopping now...')
            spider.crawler.stop()
            raise scrapy.exceptions.IgnoreRequest()
        token = AuthManager.get_access_token()
        request.headers['Authorization'] = token
        # spider MUST implement the expires_soon method
        if self._expires_soon(spider):
            AuthManager.reset_access_token(spider)

    def process_response(self, request, response, spider):
        if response.status == 401 or response.status == 429:
            spider.logger.info('Time transcurred: {}'.format((datetime.now() - AuthManager.start_time).total_seconds()))
            logging.info('{} returned for request to {}'.format(response.status, request.url))
            if not AuthManager.access_token == request.headers['Authorization'] and self._expires_soon(spider):
                AuthManager.reset_access_token(spider)
            request.headers['Authorization'] = AuthManager.get_access_token()
            return request
        return response

    def _expires_soon(self, spider):
        return spider.expires_soon(datetime.now() - AuthManager.start_time)


class AuthManager(object):
    """ Helper class for ParaguayAuthMiddleware """

    access_token = None
    start_time = None
    auth_failed = False

    @classmethod
    def get_access_token(cls):
        return cls.access_token

    @classmethod
    def reset_access_token(cls, spider):
        cls.start_time = datetime.now()
        try:
            # spider MUST implement the request_access_token method
            cls.access_token = spider.request_access_token()
        except AuthenticationFailureException:
            cls.auth_failed = True
