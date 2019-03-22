from datetime import datetime

import requests
from scrapy import Request
from scrapy.http import Headers

from kingfisher_scrapy.base_spider import BaseSpider

access_token = None

# All the Paraguay services has a auth system that is based on access token that expires after a certain amount of
# request or a certain amount of time, with this class we manage the generation and regeneration of that access token


class ParaguayBase(BaseSpider):
    request_token = 'Basic ' \
                    'ODhjYmYwOGEtMDcyMC00OGY1LWFhYWUtMWVkNzVkZmFiYzZiOjNjNjQxZGQ5LWNjN2UtNDI5ZC05NWRiLWI5ODNiNmYy' \
                    'MDY3NA== '
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }
    # The time when the last valid access token request was made
    request_time = None
    # The maximum number of request allowed by the service
    request_limit = 5000
    # The maximum time that a access token is valid
    request_time_limit = 14.0
    # The response header with the information about how many request left for the five access token
    request_limit_header = 'X-Ratelimit-Remaining'
    # Number of remaining request given the access token
    remaining_limit = None

    @staticmethod
    def get_difference_minutes(datetime_end, datetime_start):
        return (datetime_end - datetime_start).total_seconds() / 60.0

    # Generate a new access token or return the existing one if it is still valid
    def get_access_token(self, response=None, first=False):
        global access_token
        if first:
            self.remaining_limit = self.request_limit
            self.request_time = datetime.now()

        if response:
            self.remaining_limit = int(response.headers[self.request_limit_header])

        if self.remaining_limit > 5 and not first \
                and self.get_difference_minutes(datetime.now(), self.request_time) < self.request_time_limit:
            return access_token
        access_token = self.generate_access_token()
        self.request_time = datetime.now()
        self.remaining_limit = self.request_limit
        return access_token

    # Generate a new access token
    def generate_access_token(self):
        correct = False
        data_json = ''
        while not correct:
            r = requests.post('https://www.contrataciones.gov.py:443/datos/api/oauth/token',
                              headers={'Authorization': self.request_token})
            try:
                data_json = r.json()['access_token']
                correct = True
            except requests.exceptions.RequestException:
                correct = False
        return 'Bearer ' + data_json


# A custom request class to use as header the most updated access token, with this, we can have concurrent request
# and we can recover a 401 status
class AuthTokenRequest(Request):
    @property
    def headers(self):
        global access_token
        return Headers({'Authorization': access_token})

    @headers.setter
    def headers(self, value):
        pass
