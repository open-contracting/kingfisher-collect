import hashlib
import json
import logging

import requests
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.exceptions import AuthenticationFailureException


class ParaguayDNCPBaseSpider(BaseSpider):
    """ This base class contains methods used for Paraguay DNCP's
    authentication protocol.
    """

    # request limits: since we can't control when Scrapy decides to send a
    # request, values here are slighly less than real limits.
    request_time_limit = 13  # in minutes
    base_page_url = 'http://beta.dncp.gov.py/datos/api/v3/doc/search/processes?fecha_desde=2010-01-01'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'kingfisher_scrapy.middlewares.HttpProxyWithSpiderArgsMiddleware': 350,
            'kingfisher_scrapy.middlewares.ParaguayAuthMiddleware': 543,
        },
        'CONCURRENT_REQUESTS': 1,
        'DUPEFILTER_DEBUG': True,
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
        return [scrapy.Request(
            self.base_page_url,
            callback=self.parse_pages
        )]

    def parse_pages(self, response):
        if response.status == 200:
            content = json.loads(response.text)
            for url in self.get_files_to_download(content):
                yield scrapy.Request(
                    url,
                    meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
                )
            pagination = content['pagination']
            if pagination['current_page'] < pagination['total_pages'] and not self.sample:
                yield scrapy.Request(
                    (self.base_page_url + '&page={}').format(pagination['current_page'] + 1),
                    meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'},
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

    def request_access_token(self):
        """ Requests a new access token (required by ParaguayAuthMiddleware) """
        token = None
        attempt = 0
        max_attempts = self.max_attempts if hasattr(self, 'max_attempts') and self.max_attempts.isdigit() else 10
        while attempt < max_attempts and token is None:
            self.logger.info('Requesting access token, attempt {} of {}'.format(attempt + 1, max_attempts))
            r = requests.post('https://www.contrataciones.gov.py:443/datos/api/v2/oauth/token',
                              headers={'Authorization': self.request_token}, proxies=self.proxies)
            if r.status_code == 200:
                try:
                    token = r.json()['access_token']
                except requests.exceptions.RequestException:
                    self.logger.error(r)
            else:
                self.logger.error('Authentication failed. Status code: {}. {}'.format(r.status_code, r.text))
            attempt = attempt + 1
        if token is None:
            self.logger.error('Max attempts to get an access token reached.')
            raise AuthenticationFailureException()
        self.logger.info('New access token: {}'.format(token))

        return 'Bearer ' + token

    def expires_soon(self, timediff):
        """ Tells if the access token will expire soon (required by
        ParaguayAuthMiddleware)
        """
        if timediff.total_seconds() < ParaguayDNCPBaseSpider.request_time_limit * 60:
            return False
        self.logger.info('Timediff: {}'.format(timediff.total_seconds()))
        return True
