import json
from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.exceptions import AuthenticationError
from kingfisher_scrapy.util import handle_error


class ParaguayHacienda(BaseSpider):
    name = 'paraguay_hacienda'

    start_time = None
    access_token = None
    auth_failed = False
    last_request = None
    max_attempts = 5
    base_list_url = 'https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/pagos/cdp?page={}'
    release_ids = []
    request_time_limit = 14.0

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'kingfisher_scrapy.middlewares.ParaguayAuthMiddleware': 543,
        },
        'CONCURRENT_REQUESTS': 1,
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ParaguayHacienda, cls).from_crawler(crawler, *args, **kwargs)

        spider.request_token = crawler.settings.get('KINGFISHER_PARAGUAY_HACIENDA_REQUEST_TOKEN')
        spider.client_secret = crawler.settings.get('KINGFISHER_PARAGUAY_HACIENDA_CLIENT_SECRET')
        if spider.request_token is None or spider.client_secret is None:
            spider.logger.error('No request token or client secret available')
            raise scrapy.exceptions.CloseSpider('authentication_credentials_missing')

        return spider

    def start_requests(self):
        # Paraguay Hacienda has a service that return all the ids that we need to get the releases packages
        # so we first iterate over this list that is paginated
        yield scrapy.Request(
            self.base_list_url.format(1),
            # send duplicate requests when the token expired and in the continuation of last_request saved.
            dont_filter=True,
            meta={'meta': True, 'first': True}
        )

    @handle_error()
    def parse(self, response):
        data = json.loads(response.text)
        base_url = 'https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/ocds/release-package/{}'

        # If is the first URL, we need to iterate over all the pages to get all the process ids to query
        if response.request.meta['first'] and not self.sample:
            total_pages = data['meta']['totalPages']
            for page in range(2,  total_pages+1):
                yield scrapy.Request(
                    url=self.base_list_url.format(page),
                    meta={'meta': True, 'first': False},
                    dont_filter=True
                )

        # if is a meta request it means that is the page that have the process ids to query
        if response.request.meta['meta']:
            if self.sample:
                data['results'] = data['results'][:50]

            # Now that we have the ids we iterate over them, without duplicate them, and make the
            # final requests for the release_package this time
            for row in data['results']:
                if row['idLlamado'] and row['idLlamado'] not in self.release_ids:
                    self.release_ids.append(row['idLlamado'])
                    yield scrapy.Request(
                        url=base_url.format(row['idLlamado']),
                        meta={'meta': False, 'first': False,
                              'kf_filename': 'release-{}.json'.format(row['idLlamado'])},
                        dont_filter=True
                    )
        else:
            yield self.build_file_from_response(response, response.request.meta['kf_filename'],
                                                data_type='release_package')

    def request_access_token(self):
        """ Requests a new access token """
        attempt = 0
        self.start_time = datetime.now()
        self.logger.info('Requesting access token, attempt {} of {}'.format(attempt + 1, self.max_attempts))
        payload = {"clientSecret": self.client_secret}

        return scrapy.Request(
            "https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/auth/token",
            method='POST',
            headers={"Authorization": self.request_token, "Content-Type": "application/json"},
            body=json.dumps(payload),
            meta={'attempt': attempt + 1, 'auth': False},
            callback=self.parse_access_token,
            dont_filter=True,
            priority=1000
        )

    def parse_access_token(self, response):
        if self.is_http_success(response):
            r = json.loads(response.text)
            token = r.get('accessToken')
            if token:
                self.logger.info('New access token: {}'.format(token))
                self.access_token = 'Bearer ' + token
                # continue scraping where it stopped after getting the token
                yield self.last_request
            else:
                attempt = response.request.meta['attempt']
                if attempt == self.max_attempts:
                    self.logger.error('Max attempts to get an access token reached.')
                    self.auth_failed = True
                    raise AuthenticationError()
                else:
                    self.logger.info('Requesting access token, attempt {} of {}'.format(
                        attempt + 1,
                        self.max_attempts)
                    )
                    return scrapy.Request(
                        "https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/auth/token",
                        method='POST',
                        headers={"Authorization": self.request_token, "Content-Type": "application/json"},
                        body=response.request.body,
                        meta={'attempt': attempt + 1, 'auth': False},
                        callback=self.parse_access_token,
                        dont_filter=True,
                        priority=1000
                    )
        else:
            self.logger.error('Authentication failed. Status code: {}'.format(response.status))
            self.auth_failed = True
            raise AuthenticationError()

    def expires_soon(self, time_diff):
        """ Tells if the access token will expire soon (required by
        ParaguayAuthMiddleware)
        """
        if time_diff.total_seconds() < ParaguayHacienda.request_time_limit * 60:
            return False
        self.logger.info('Time_diff: {}'.format(time_diff.total_seconds()))
        return True
