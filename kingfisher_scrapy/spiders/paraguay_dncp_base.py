import json
from datetime import datetime, timedelta

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.exceptions import AccessTokenError, MissingEnvVarError
from kingfisher_scrapy.util import components, handle_http_error, parameters, replace_parameters


class ParaguayDNCPBase(SimpleSpider):
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'kingfisher_scrapy.downloadermiddlewares.ParaguayAuthMiddleware': 543,
        },
        'CONCURRENT_REQUESTS': 1,
    }

    # BaseSpider
    date_format = 'datetime'
    default_from_date = '2010-01-01T00:00:00'
    date_required = True

    # request limits: since we can't control when Scrapy decides to send a
    # request, values here are slightly less than real limits.
    start_time = None
    access_token = None
    auth_failed = False
    last_requests = []
    request_time_limit = 13  # in minutes
    base_url = 'https://contrataciones.gov.py/datos/api/v3/doc'
    auth_url = f'{base_url}/oauth/token'
    request_token = None
    max_attempts = 10

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        spider.request_token = crawler.settings.get('KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN')

        if spider.request_token is None:
            raise MissingEnvVarError('KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN is not set.')

        return spider

    def start_requests(self):
        for url in self.urls_builder():
            yield self.build_request(
                url,
                formatter=parameters('fecha_desde'),
                # send duplicate requests when the token expired and in the continuation of last_requests saved.
                dont_filter=True,
                callback=self.parse_pages
            )

    def urls_builder(self):
        # ElasticSearch doesn't allow search sizes greater than 10000, so we request half-month at the time.
        interval = timedelta(days=15)
        end_date = self.until_date
        # In reverse chronological order
        while end_date > self.from_date:
            # If there is less than or equal to one interval left, start from the `from_date`.
            if end_date - self.from_date <= interval:
                start_date = self.from_date
            else:
                start_date = end_date - interval
            url = f'{self.base_url}/search/processes?tipo_fecha=fecha_release&' \
                  f'fecha_desde={start_date.strftime(self.date_format)}-04:00&' \
                  f'fecha_hasta={end_date.strftime(self.date_format)}-04:00&items_per_page=10000'
            end_date = start_date - timedelta(seconds=1)
            yield url

    def request_access_token(self):
        """ Requests a new access token """
        attempt = 0
        self.start_time = datetime.now()
        self.logger.info('Requesting access token, attempt %s of %s', attempt + 1, self.max_attempts)

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
            r = response.json()
            token = r.get('access_token')
            if token:
                self.logger.info('New access token: %s', token)
                self.access_token = token
                # continue scraping where it stopped after getting the token
                while self.last_requests:
                    yield self.last_requests.pop(0)
            else:
                attempt = response.request.meta['attempt']
                if attempt == self.max_attempts:
                    self.logger.error('Max attempts to get an access token reached.')
                    self.auth_failed = True
                    raise AccessTokenError()
                else:
                    self.logger.info('Requesting access token, attempt %s of %s', attempt + 1, self.max_attempts)
                    yield scrapy.Request(
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
            self.logger.error('Authentication failed. Status code: %s', response.status)
            self.auth_failed = True
            raise AccessTokenError()

    @handle_http_error
    def parse_pages(self, response):
        content = response.json()
        for url in self.get_files_to_download(content):
            yield self.build_request(url, formatter=components(-1), dont_filter=True)
        pagination = content['pagination']
        if pagination['current_page'] < pagination['total_pages']:
            page = pagination['current_page'] + 1
            url = replace_parameters(response.request.url, page=page)
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
        if time_diff.total_seconds() < ParaguayDNCPBase.request_time_limit * 60:
            return False
        self.logger.info('Time_diff: %s', time_diff.total_seconds())
        return True
