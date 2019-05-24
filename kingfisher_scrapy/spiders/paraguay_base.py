import scrapy
import requests
import logging

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.exceptions import AuthenticationFailureException


class ParaguayDNCPBaseSpider(BaseSpider):
    """ This base class contains methods used for Paraguay DNCP's
    authentication protocol.
    """

    # request limits: since we can't control when Scrapy decides to send a
    # request, values here are slighly less than real limits.
    request_time_limit = 13  # in minutes
    request_limit = 4500

    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'DOWNLOADER_MIDDLEWARES': {
            'kingfisher_scrapy.middlewares.ParaguayAuthMiddleware': 543
        },
        'HTTPERROR_ALLOW_ALL': True,
        'CONCURRENT_REQUESTS': 1
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ParaguayDNCPBaseSpider, cls).from_crawler(crawler, *args, **kwargs)

        spider.request_token = crawler.settings.get('KINGFISHER_PARAGUAY_DNCP_REQUEST_TOKEN')
        if spider.request_token is None:
            logging.error('No request token available')
            raise scrapy.exceptions.CloseSpider('authentication_credentials_missing')

        return spider

    def request_access_token(self):
        """ Requests a new access token (required by ParaguayAuthMiddleware) """
        token = None
        attempt = 0
        max_attempts = 5
        while attempt < max_attempts and token is None:
            self.logger.info('Requesting access token, attempt {} of {}'.format(attempt + 1, max_attempts))
            r = requests.post('https://www.contrataciones.gov.py:443/datos/api/v2/oauth/token',
                              headers={'Authorization': self.request_token})
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

    def expires_soon(self, count, timediff):
        """ Tells if the access token will expire soon (required by
        ParaguayAuthMiddleware)
        """
        if timediff.total_seconds() < ParaguayDNCPBaseSpider.request_time_limit * 60 and count < ParaguayDNCPBaseSpider.request_limit:
            return False
        self.logger.info('Count: {}, Timediff: {}'.format(count, timediff.total_seconds()))
        return True
