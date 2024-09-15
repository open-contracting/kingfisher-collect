import json
from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spiders import BaseSpider
from kingfisher_scrapy.exceptions import AccessTokenError, MissingEnvVarError
from kingfisher_scrapy.util import components, handle_http_error, parameters


class ParaguayHacienda(BaseSpider):
    """
    Domain
      Ministerio de Hacienda
    Environment variables
      KINGFISHER_PARAGUAY_HACIENDA_REQUEST_TOKEN
        To get an API account and request token go to https://datos.hacienda.gov.py/aplicaciones/new.
      KINGFISHER_PARAGUAY_HACIENDA_CLIENT_SECRET
        Your client secret generated.
    Swagger API documentation
      https://datos.hacienda.gov.py/odmh-api-v1/api-docs/
    """
    name = 'paraguay_hacienda'
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOADER_MIDDLEWARES': {
            'kingfisher_scrapy.downloadermiddlewares.ParaguayAuthMiddleware': 543,
        },
    }

    # BaseSpider
    dont_truncate = True

    # ParaguayAuthMiddleware
    access_token = None
    access_token_scheduled_at = None
    # The maximum age is less than the API's limit, since we don't precisely control Scrapy's scheduler.
    access_token_maximum_age = 14 * 60
    access_token_request_failed = False
    requests_backlog = []

    # Local
    max_access_token_attempts = 5
    url_prefix = 'https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/'
    list_url_prefix = f'{url_prefix}pagos/cdp?page='
    release_ids = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        spider.request_token = crawler.settings.get('KINGFISHER_PARAGUAY_HACIENDA_REQUEST_TOKEN')
        spider.client_secret = crawler.settings.get('KINGFISHER_PARAGUAY_HACIENDA_CLIENT_SECRET')
        if spider.request_token is None or spider.client_secret is None:
            raise MissingEnvVarError('KINGFISHER_PARAGUAY_HACIENDA_REQUEST_TOKEN and/or '
                                     'KINGFISHER_PARAGUAY_HACIENDA_CLIENT_SECRET is not set.')

        return spider

    def start_requests(self):
        # Paraguay Hacienda has a service that return all the ids that we need to get the releases packages
        # so we first iterate over this list that is paginated
        yield self.build_request(
            f'{self.list_url_prefix}1',
            formatter=parameters('page'),
            meta={
                'meta': True,
                'first': True,
            },
            # send duplicate requests when the token expired and in the continuation of requests_backlog saved.
            dont_filter=True,
        )

    @handle_http_error
    def parse(self, response):
        package_url_prefix = f'{self.url_prefix}ocds/release-package/'

        data = response.json()

        # If is the first URL, we need to iterate over all the pages to get all the process ids to query
        if response.request.meta['first']:
            total = data['meta']['totalPages']
            for page in range(2,  total + 1):
                yield self.build_request(
                    f'{self.list_url_prefix}{page}',
                    formatter=parameters('page'),
                    meta={
                        'meta': True,
                        'first': False,
                    },
                    dont_filter=True
                )

        # if is a meta request it means that is the page that have the process ids to query
        if response.request.meta['meta']:
            # Now that we have the ids we iterate over them, without duplicate them, and make the
            # final requests for the release_package this time
            for row in data['results']:
                if row['idLlamado'] and row['idLlamado'] not in self.release_ids:
                    self.release_ids.append(row['idLlamado'])
                    yield self.build_request(
                        f'{package_url_prefix}{row["idLlamado"]}',
                        formatter=components(-1),
                        meta={
                            'meta': False,
                            'first': False,
                        },
                        dont_filter=True
                    )
        else:
            yield self.build_file_from_response(response, data_type='release_package')

    def build_access_token_request(self, body=None, attempt=0):
        self.logger.info('Requesting access token, attempt %s of %s', attempt + 1, self.max_access_token_attempts)

        if body is None:
            body = json.dumps({"clientSecret": self.client_secret})

        self.access_token_scheduled_at = datetime.now()

        return scrapy.Request(
            f'{self.url_prefix}auth/token',
            method='POST',
            headers={'Authorization': self.request_token, 'Content-Type': 'application/json'},
            body=body,
            meta={'attempt': attempt + 1, 'auth': False},
            callback=self.parse_access_token,
            dont_filter=True,
            priority=1000
        )

    def parse_access_token(self, response):
        if self.is_http_success(response):
            token = response.json().get('accessToken')
            if token:
                self.logger.info('New access token: %s', token)
                self.access_token = f'Bearer {token}'
                # continue scraping where it stopped after getting the token
                while self.requests_backlog:
                    yield self.requests_backlog.pop(0)
            else:
                attempt = response.request.meta['attempt']
                if attempt == self.max_access_token_attempts:
                    self.logger.error('Max attempts to get an access token reached.')
                    self.access_token_request_failed = True
                    raise AccessTokenError
                else:
                    yield self.build_access_token_request(response.request.body, attempt=attempt)
        else:
            self.logger.error('Authentication failed. Status code: %s', response.status)
            self.access_token_request_failed = True
            raise AccessTokenError
