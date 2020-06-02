import json
from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.exceptions import AuthenticationError
from kingfisher_scrapy.util import components, handle_error, parameters


class ParaguayDNCPBaseSpider(SimpleSpider):
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
    base_page_url = f'{base_url}/search/processes?fecha_desde=2010-01-01'
    auth_url = f'{base_url}/oauth/token'
    request_token = None
    max_attempts = 10
    data_type = None
    default_from_date = '2010-01-01T00:00:00'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'kingfisher_scrapy.middlewares.ParaguayAuthMiddleware': 543,
        },
        'CONCURRENT_REQUESTS': 1,
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ParaguayDNCPBaseSpider, cls).from_crawler(crawler, date_format='datetime',
                                                                 *args, **kwargs)

        spider.request_token = crawler.settings.get('KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN')

        if spider.request_token is None:
            spider.logger.error('KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN is not set.')
            raise scrapy.exceptions.CloseSpider('authentication_credentials_missing')

        return spider

    def start_requests(self):
        if self.from_date:
            from_date = self.from_date.strftime(self.date_format)
            self.base_page_url = '{}/search/processes?tipo_fecha=fecha_release&fecha_desde={}'\
                .format(self.base_url, from_date)
        yield self.build_request(
            self.base_page_url,
            formatter=parameters('fecha_desde'),
            meta={
                'from_date': from_date,
            },
            # send duplicate requests when the token expired and in the continuation of last_request saved.
            dont_filter=True,
            callback=self.parse_pages
        )

    def request_access_token(self):
        """ Requests a new access token """
        attempt = 0
        self.start_time = datetime.now()
        self.logger.info(f'Requesting access token, attempt {attempt + 1} of {self.max_attempts}')

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
        if self.is_http_success(response):
            r = json.loads(response.text)
            token = r.get('access_token')
            if token:
                self.logger.info(f'New access token: {token}')
                self.access_token = token
                # continue scraping where it stopped after getting the token
                yield self.last_request
            else:
                attempt = response.request.meta['attempt']
                if attempt == self.max_attempts:
                    self.logger.error('Max attempts to get an access token reached.')
                    self.auth_failed = True
                    raise AuthenticationError()
                else:
                    self.logger.info(f'Requesting access token, attempt {attempt + 1} of {self.max_attempts}')
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
            self.logger.error(f'Authentication failed. Status code: {response.status}')
            self.auth_failed = True
            raise AuthenticationError()

    @handle_error
    def parse_pages(self, response):
        content = json.loads(response.text)
        for url in self.get_files_to_download(content):
            yield self.build_request(url, formatter=components(-1), dont_filter=True)
        pagination = content['pagination']
        if pagination['current_page'] < pagination['total_pages'] and not self.sample:
            page = pagination['current_page'] + 1
            url = f'{self.base_page_url}&page={page}'
            yield self.build_request(
                url,
                formatter=parameters('fecha_desde', 'page'),
                dont_filter=True,
                callback=self.parse_pages
            )

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
        self.logger.info(f'Time_diff: {time_diff.total_seconds()}')
        return True
