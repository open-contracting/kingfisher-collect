import json
import logging
from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.exceptions import AuthenticationFailureException


class ParaguayDNCPBaseSpider(BaseSpider):
    """ This base class contains methods used for Paraguay DNCP's
    authentication protocol.
    """

    # request limits: since we can't control when Scrapy decides to send a
    # request, values here are slighly less than real limits.
    start_time = None
    access_token = None
    auth_failed = False
    last_request = None
    request_time_limit = 13  # in minutes
    base_url = 'https://contrataciones.gov.py/datos/api/v3/doc'
    base_page_url = '{}/search/processes?fecha_desde=2010-01-01'.format(base_url)
    auth_url = '{}/oauth/token'.format(base_url)
    request_token = None
    max_attempts = 10
    data_type = None

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'kingfisher_scrapy.middlewares.HttpProxyWithSpiderArgsMiddleware': 350,
            'kingfisher_scrapy.middlewares.ParaguayAuthMiddleware': 543,
        },
        'CONCURRENT_REQUESTS': 1,
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ParaguayDNCPBaseSpider, cls).from_crawler(crawler, *args, **kwargs)

        spider.request_token = crawler.settings.get('KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN')

        if spider.request_token is None:
            logging.error('No request token available')
            raise scrapy.exceptions.CloseSpider('authentication_credentials_missing')

        spider.proxies = None
        if spider.https_proxy:
            spider.proxies = {'https': spider.https_proxy}

        return spider

    def start_requests(self):
        yield scrapy.Request(
            self.base_page_url,
            # send duplicate requests when the token expired and in the continuation of last_request saved.
            dont_filter=True,
            callback=self.parse_pages
        )

    def request_access_token(self):
        """ Requests a new access token """
        attempt = 0
        self.start_time = datetime.now()
        self.logger.info('Requesting access token, attempt {} of {}'.format(attempt + 1, self.max_attempts))

        return scrapy.Request(
            self.auth_url,
            method='POST',
            headers={'accept': 'application/json', 'Content-Type': 'application/json'},
            body=json.dumps({'request_token': self.request_token}),
            meta={'attempt': attempt + 1, 'auth': False},
            callback=self.parse_access_token,
            dont_filter=True,
            priority=1000
        )

    def parse_access_token(self, response):
        if response.status == 200:
            r = json.loads(response.text)
            token = r.get('access_token')
            if token:
                self.logger.info('New access token: {}'.format(token))
                self.access_token = token
                # continue scraping where it stopped after getting the token
                yield self.last_request
            else:
                attempt = response.request.meta['attempt']
                if attempt == self.max_attempts:
                    self.logger.error('Max attempts to get an access token reached.')
                    self.auth_failed = True
                    raise AuthenticationFailureException()
                else:
                    self.logger.info('Requesting access token, attempt {} of {}'.format(
                        attempt + 1,
                        self.max_attempts)
                    )
                    return scrapy.Request(
                        self.auth_url,
                        method='POST',
                        headers={'accept': 'application/json', 'Content-Type': 'application/json'},
                        body=json.dumps({'request_token': self.request_token}),
                        meta={'attempt': attempt + 1, 'auth': False},
                        callback=self.parse_access_token,
                        dont_filter=True,
                        priority=1000
                    )
        else:
            self.logger.error('Authentication failed. Status code: {}'.format(response.status))
            self.auth_failed = True
            raise AuthenticationFailureException()

    def parse_pages(self, response):
        if response.status == 200:
            content = json.loads(response.text)
            for url in self.get_files_to_download(content):
                yield scrapy.Request(
                    url,
                    dont_filter=True,
                    meta={'kf_filename': url.split('/')[-1] + '.json'}
                )
            pagination = content['pagination']
            if pagination['current_page'] < pagination['total_pages'] and not self.sample:
                url = '{}&page={}'.format(self.base_page_url, pagination['current_page'] + 1)
                yield scrapy.Request(
                    url,
                    dont_filter=True,
                    callback=self.parse_pages
                )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }

    def parse(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(
                response,
                response.request.meta['kf_filename'],
                data_type=self.data_type
            )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }

    def get_files_to_download(self, content):
        """ Override this
        """
        yield from ()

    def expires_soon(self, time_diff):
        """ Tells if the access token will expire soon (required by
        ParaguayAuthMiddleware)
        """
        if time_diff.total_seconds() < ParaguayDNCPBaseSpider.request_time_limit * 60:
            return False
        self.logger.info('Time_diff: {}'.format(time_diff.total_seconds()))
        return True
