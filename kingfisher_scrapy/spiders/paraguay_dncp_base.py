import json
from abc import abstractmethod
from datetime import datetime, timedelta

import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.exceptions import AccessTokenError, MissingEnvVarError
from kingfisher_scrapy.util import components, handle_http_error, parameters, replace_parameters


class ParaguayDNCPBase(SimpleSpider):
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOADER_MIDDLEWARES': {
            'kingfisher_scrapy.downloadermiddlewares.ParaguayAuthMiddleware': 543,
        },
    }

    # BaseSpider
    date_format = 'datetime'
    default_from_date = '2010-01-01T00:00:00'
    date_required = True

    # ParaguayAuthMiddleware
    access_token = None
    access_token_scheduled_at = None
    # The maximum age is less than the API's limit, since we don't precisely control Scrapy's scheduler.
    access_token_maximum_age = 13 * 60
    access_token_request_failed = False
    requests_backlog = []

    # Local
    max_attempts = 10
    url_prefix = 'https://contrataciones.gov.py/datos/api/v3/doc/'

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
                # send duplicate requests when the token expired and in the continuation of requests_backlog saved.
                dont_filter=True,
                callback=self.parse_pages
            )

    def urls_builder(self):
        # ElasticSearch doesn't allow search sizes greater than 10000, so we request half-month at the time.
        interval = timedelta(days=30)
        end_date = self.until_date
        # In reverse chronological order
        while end_date > self.from_date:
            # If there is less than or equal to one interval left, start from the `from_date`.
            if end_date - self.from_date <= interval:
                start_date = self.from_date
            else:
                start_date = end_date - interval
            # We request active/complete tenders and planned ones separately to ensure we don't exceed the 10000
            # results per request limit.
            url_base = f'{self.url_prefix}search/processes?fecha_desde={start_date.strftime(self.date_format)}' \
                       f'-04:00&fecha_hasta={end_date.strftime(self.date_format)}-04:00&items_per_page=10000 '
            # We request the active or successful tenders by using the "publicacion_llamado" filter.
            url_tender = f'{url_base}&tipo_fecha=publicacion_llamado'
            # And the planned ones with the "fecha_release" and tender.id=planned filters.
            url_planning = f'{url_base}&tender.id=planned&tipo_fecha=fecha_release'
            end_date = start_date - timedelta(seconds=1)
            yield from [url_tender, url_planning]

    def build_access_token_request(self, attempt=0):
        self.logger.info('Requesting access token, attempt %s of %s', attempt + 1, self.max_attempts)

        self.access_token_scheduled_at = datetime.now()

        return scrapy.Request(
            f'{self.url_prefix}oauth/token',
            method='POST',
            headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
            body=json.dumps({'request_token': self.request_token}),
            meta={'attempt': attempt + 1, 'auth': False},
            callback=self.parse_access_token,
            dont_filter=True,
            priority=1000
        )

    def parse_access_token(self, response):
        if self.is_http_success(response):
            token = response.json().get('access_token')
            if token:
                self.logger.info('New access token: %s', token)
                self.access_token = token
                # continue scraping where it stopped after getting the token
                while self.requests_backlog:
                    yield self.requests_backlog.pop(0)
            else:
                attempt = response.request.meta['attempt']
                if attempt == self.max_attempts:
                    self.logger.error('Max attempts to get an access token reached.')
                    self.access_token_request_failed = True
                    raise AccessTokenError()
                else:
                    yield self.build_access_token_request(attempt=attempt)
        else:
            self.logger.error('Authentication failed. Status code: %s', response.status)
            self.access_token_request_failed = True
            raise AccessTokenError()

    @handle_http_error
    def parse_pages(self, response):
        data = response.json()
        for url in self.get_files_to_download(data):
            yield self.build_request(url, formatter=components(-1), dont_filter=True)
        pagination = data['pagination']
        if pagination['current_page'] < pagination['total_pages']:
            page = pagination['current_page'] + 1
            url = replace_parameters(response.request.url, page=page)
            yield self.build_request(
                url,
                formatter=parameters('fecha_desde', 'page'),
                dont_filter=True,
                callback=self.parse_pages
            )

    @abstractmethod
    def get_files_to_download(self, data):
        pass
