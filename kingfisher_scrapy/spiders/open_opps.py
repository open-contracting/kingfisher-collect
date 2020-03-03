import hashlib
import json
from datetime import datetime, timedelta
from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.exceptions import AuthenticationFailureException


class OpenOpps(BaseSpider):
    name = 'open_opps'

    access_token = None
    api_limit = 10000  # OpenOpps API limit for search results
    page_size = 1000
    page_format = 'json'
    ordering = 'releasedate'

    base_page_url = \
        'https://api.openopps.com/api/ocds/?' \
        'format={}&ordering={}&page_size={}&releasedate__gte={}&releasedate__lte={}'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'kingfisher_scrapy.middlewares.OpenOppsAuthMiddleware': 543,
        },
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(OpenOpps, cls).from_crawler(crawler, *args, **kwargs)

        spider.username = crawler.settings.get('KINGFISHER_OPENOPPS_USERNAME')
        spider.password = crawler.settings.get('KINGFISHER_OPENOPPS_PASSWORD')
        if spider.username is None or spider.password is None:
            raise scrapy.exceptions.CloseSpider('authentication_credentials_missing')

        return spider

    def start_requests(self):
        """ Start requesting access token """
        yield scrapy.Request(
            url="https://api.openopps.com/api/api-token-auth/",
            method='POST',
            headers={"Accept": "*/*", "Content-Type": "application/json"},
            body=json.dumps({"username": self.username, "password": self.password}),
            meta={'token_request': True},
            callback=self.parse_access_token
        )

    def parse_access_token(self, response):
        if response.status == 200:
            r = json.loads(response.text)
            token = r.get('token')
            if token:
                self.logger.info('New access token: {}'.format(token))
                self.access_token = 'JWT ' + token
                """ Start """
                return self.start_requests_pages()
            else:
                self.logger.error(
                    'Authentication failed. Status code: {}. {}'.format(response.status, response.text))
                raise AuthenticationFailureException()
        else:
            self.logger.error(
                'Authentication failed. Status code: {}. {}'.format(response.status, response.text))
            raise AuthenticationFailureException()

    def start_requests_pages(self):
        # Use larger ranges for filters with less than (api_limit) search results
        if not self.sample:
            release_date_gte_list = ['', '2009-01-01', '2010-01-01', '2010-07-01']
            release_date_lte_list = ['2008-12-31', '2009-12-31', '2010-06-30', '2010-12-31']

            for i in range(0, 4):
                yield scrapy.Request(
                    url=self.base_page_url.format(
                        self.page_format,
                        self.ordering,
                        self.page_size,
                        release_date_gte_list[i],
                        release_date_lte_list[i]
                    ),
                    headers={"Accept": "*/*", "Content-Type": "application/json"},
                )

        # Use smaller ranges for filters with more than (api_limit) search results
        for year in range(2011, datetime.now().year + 1):
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, datetime.now().month, datetime.now().day) \
                if year == datetime.now().year else datetime(year, 12, 31)
            date_list = [(start_date + timedelta(days=d)).strftime("%Y-%m-%d")
                         for d in range((end_date - start_date).days + 1)]

            for date in date_list:
                release_date_gte = date
                release_date_lte = date
                yield scrapy.Request(
                    url=self.base_page_url.format(
                        self.page_format,
                        self.ordering,
                        self.page_size,
                        release_date_gte,
                        release_date_lte
                    ),
                    headers={"Accept": "*/*", "Content-Type": "application/json"},
                    meta={"release_date": date},
                )

                if self.sample:
                    break
            if self.sample:
                break

    def parse(self, response):
        if response.status == 200:
            results = json.loads(response.text)
            count = results.get('count')
            if count <= 10000:

                for data in results.get('results'):
                    json_data = data.get('json')
                    if not json_data:
                        continue
                    json_uri = json_data.get('uri')
                    if not json_uri:
                        json_uri = response.request.url + data.get('ocid')
                    self.save_data_to_disk(
                        json_data,
                        filename=hashlib.md5(json_uri.encode('utf-8')).hexdigest() + '.json',
                        url=json_uri,
                        data_type='release_package'
                    )
            else:
                if 'release_date' in response.request.meta and response.request.meta['release_date']:
                    parts = int(ceil(count / self.api_limit))  # parts we split a day with more than 10K data
                    split_h = int(ceil(24 / parts))  # hours we split
                    date = response.request.meta['release_date']
                    date = datetime.strptime(date, "%Y-%m-%d")
                    start_hour_list = [(date + timedelta(hours=H)
                                        ).strftime("%Y-%m-%dT%H:%M:%S") for H in range(0, 24, split_h)]
                    end_hour_list = [(date + timedelta(hours=H, minutes=59, seconds=59)
                                      ).strftime("%Y-%m-%dT%H:%M:%S") for H in range(split_h-1, 24, split_h)]

                    # if parts is not a divisor of 24
                    if len(start_hour_list) != len(end_hour_list):
                        end_hour_list.append(response.request.meta['release_date'] + 'T23:59:59')

                    self.logger.info('Changing filters, split in {}: {}.'.format(parts, response.request.url))
                    for i in range(0, parts):
                        yield scrapy.Request(
                            url=self.base_page_url.format(
                                self.page_format,
                                self.ordering,
                                self.page_size,
                                start_hour_list[i],
                                end_hour_list[i]
                            ),
                            headers={"Accept": "*/*", "Content-Type": "application/json"},
                            meta={"release_date": date},
                        )

            if not self.sample:
                next_url = results.get('next')
                if next_url:
                    yield scrapy.Request(
                        url=next_url,
                        headers={"Accept": "*/*", "Content-Type": "application/json"},
                    )
        else:
            if response.status != 500:
                yield {
                    'success': False,
                    'url': response.request.url,
                    'errors': {'http_code': response.status}
                }
