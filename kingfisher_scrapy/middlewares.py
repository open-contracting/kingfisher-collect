# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import logging
from datetime import datetime

import scrapy


class HttpProxyWithSpiderArgsMiddleware:

    def __init__(self, spider):
        logging.info('Using HttpProxyWithSpiderArgsMiddleware.')
        if not spider.http_proxy and not spider.https_proxy:
            logging.warning('No proxy arguments have been set!')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider)

    def process_request(self, request, spider):
        if request.url.startswith('https:') and spider.https_proxy:
            request.meta['proxy'] = spider.https_proxy
        elif request.url.startswith('http:') and spider.http_proxy:
            request.meta['proxy'] = spider.http_proxy


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
        logging.info('Initialized authentication middleware with spider: {}.'.format(spider.name))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider)

    def process_request(self, request, spider):
        if 'auth' in request.meta and request.meta['auth'] is not None and not request.meta['auth']:
            return
        if spider.auth_failed:
            logging.error('Fatal: no authentication token, stopping now...')
            spider.crawler.stop()
            raise scrapy.exceptions.IgnoreRequest()
        request.headers['Authorization'] = spider.access_token
        if self._expires_soon(spider):
            # spider MUST implement the request_access_token method
            spider.request_access_token()

    def process_response(self, request, response, spider):
        if response.status == 401 or response.status == 429:
            spider.logger.info('Time transcurred: {}'.format((datetime.now() - spider.start_time).total_seconds()))
            logging.info('{} returned for request to {}'.format(response.status, request.url))
            if not spider.access_token == request.headers['Authorization'] and self._expires_soon(spider):
                spider.request_access_token()
            request.headers['Authorization'] = spider.access_token
            return request
        return response

    @staticmethod
    def _expires_soon(spider):
        # spider MUST implement the expires_soon method
        return spider.expires_soon(datetime.now() - spider.start_time) if spider.start_time else True


class OpenOppsAuthMiddleware:
    """Downloader middleware that intercepts requests and adds the token
    for OpenOpps scraper."""

    @staticmethod
    def process_request(request, spider):
        if 'token_request' in request.meta and request.meta['token_request']:
            return
        request.headers['Authorization'] = spider.access_token
