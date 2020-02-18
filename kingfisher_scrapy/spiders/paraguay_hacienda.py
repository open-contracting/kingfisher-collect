import json

import requests
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.exceptions import AuthenticationFailureException


class ParaguayHacienda(BaseSpider):

    name = 'paraguay_hacienda'

    base_list_url = 'https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/pagos/cdp?page={}'
    release_ids = []
    request_limit = 10000
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
        yield scrapy.Request(self.base_list_url.format(1), meta={'meta': True, 'first': True})

    def parse(self, response):
        if response.status == 200:

            # When we have a 200 response, we update the number of remaining request calling the get access token method
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
                yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type='release_package')

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }

    def request_access_token(self):
        """ Requests an access token (required by ParaguayAuthMiddleware). """
        token = None
        attempt = 0
        max_attempts = 5
        while attempt < max_attempts and token is None:
            self.logger.info('Requesting access token, attempt {} of {}'.format(attempt + 1, max_attempts))
            r = requests.post("https://datos.hacienda.gov.py:443/odmh-api-v1/rest/api/v1/auth/token",
                              headers={"Authorization": self.request_token},
                              json={"clientSecret": "%s" % self.client_secret})
            if r.status_code == 200:
                try:
                    token = r.json()['accessToken']
                except requests.exceptions.RequestException:
                    self.logger.error(r)
            else:
                self.logger.error('Authentication failed. Status code: {}. {}'.format(r.status_code, r.text))
            attempt = attempt + 1
        if token is None:
            self.logger.error('Max attempts to get an access token reached.')
            raise AuthenticationFailureException()
        self.logger.info('New access token: {}'.format(token))
        return token

    def expires_soon(self, count, timediff):
        """ Tells if current access token will expire soon (required by
        ParaguayAuthMiddleware)
        """
        if timediff.total_seconds() < ParaguayHacienda.request_time_limit * 60 and count < ParaguayHacienda.request_limit:
            return False
        self.logger.info('Count: {}, Timediff: {}'.format(count, timediff.total_seconds()))
        return True
