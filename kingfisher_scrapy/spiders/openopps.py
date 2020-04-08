import hashlib
import json
from datetime import datetime, timedelta
from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.exceptions import AuthenticationFailureException


class OpenOpps(BaseSpider):
    """
    API documentation
      https://docs.google.com/document/d/1u0da3BTU7fBFjX6i7j_tKXa1YwdXL7hY4Kw9GdsaAr0/edit
    Swagger API documentation
      https://api.openopps.com/api/schema/
    Spider arguments
      sample
        Download only data released on 2011-01-01.
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2011-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    Environment variables
      KINGFISHER_OPENOPPS_USERNAME
        To get an API account, contact contact@openopps.com.
      KINGFISHER_OPENOPPS_PASSWORD
        Your API account password.
    """
    name = 'openopps'

    access_token = None
    api_limit = 10000  # OpenOpps API limit for search results
    download_delay = 1

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
            spider.logger.error('Please set the environment variables '
                                'KINGFISHER_OPENOPPS_USERNAME and KINGFISHER_OPENOPPS_PASSWORD')
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
                """ Start requests """
                return self.start_requests_pages()
            else:
                self.logger.error(
                    'Authentication failed. Status code: {}. {}'.format(response.status, response.text))
                raise AuthenticationFailureException()
        else:
            self.logger.error(
                'Authentication failed. Status code: {}. {}'.format(response.status, response.text))
            raise AuthenticationFailureException()

    def request_date_list(self, start_date, end_date, search_h):
        date_list = [(start_date + timedelta(days=d)).strftime("%Y-%m-%d")
                     for d in range((end_date - start_date).days + 1)]

        for date in date_list:
            release_date_gte = date
            release_date_lte = date
            yield scrapy.Request(
                url=self.base_page_url.format(
                    release_date_gte,
                    release_date_lte
                ),
                headers={"Accept": "*/*", "Content-Type": "application/json"},
                meta={"release_date": date, "search_h": search_h},
            )

    def start_requests_pages(self):
        page_size = 1000
        page_format = 'json'
        ordering = 'releasedate'
        search_h = 24  # start splitting one day search
        self.base_page_url = self.base_page_url.format(page_format, ordering, page_size, '{}', '{}')

        # Case if we want to download a sample
        if self.sample:
            date = datetime(2011, 1, 1)
            yield from self.request_date_list(date, date, search_h)
        else:
            # Case if we have date range parameters
            if self.from_date or self.until_date:
                try:
                    if not self.from_date:
                        self.from_date = '2011-01-01'
                    if not self.until_date:
                        self.until_date = datetime.now().strftime("%Y-%m-%d")
                    start_date = datetime.strptime(self.from_date, "%Y-%m-%d")
                    end_date = datetime.strptime(self.until_date, "%Y-%m-%d")

                except ValueError as e:
                    self.logger.error(e.args)
                    self.logger.info('See API documentation for date format.')
                    return

                yield from self.request_date_list(start_date, end_date, search_h)
            else:
                # Use larger ranges for filters with less than (api_limit) search results
                release_date_gte_list = ['', '2009-01-01', '2010-01-01', '2010-07-01']
                release_date_lte_list = ['2008-12-31', '2009-12-31', '2010-06-30', '2010-12-31']

                for i in range(len(release_date_gte_list)):
                    yield scrapy.Request(
                        url=self.base_page_url.format(
                            release_date_gte_list[i],
                            release_date_lte_list[i]
                        ),
                        headers={"Accept": "*/*", "Content-Type": "application/json"},
                        meta={"release_date": release_date_gte_list[i], "search_h": search_h},
                    )

                # Use smaller ranges (day by day) for filters with more than (api_limit) search results
                for year in range(2011, datetime.now().year + 1):
                    start_date = datetime(year, 1, 1)
                    end_date = datetime(year, datetime.now().month, datetime.now().day) \
                        if year == datetime.now().year else datetime(year, 12, 31)
                    yield from self.request_date_list(start_date, end_date, search_h)

    def parse(self, response):
        if response.status == 200:
            results = json.loads(response.text)
            count = results['count']
            release_date = response.request.meta['release_date']  # date used for the search
            search_h = response.request.meta['search_h']  # hour range used for the search

            # Counts response and range hour split control
            if count <= self.api_limit or search_h == 1:
                # Data type changed to release package list in order to have fewer files
                all_data = []
                for data in results['results']:
                    json_data = data['json']
                    if json_data:
                        all_data.append(json_data)

                if all_data:
                    self.save_data_to_disk(
                        all_data,
                        filename=hashlib.md5(response.request.url.encode('utf-8')).hexdigest() + '.json',
                        url=response.request.url,
                        data_type='release_package_list'
                    )
                    if self.sample:
                        return

                next_url = results.get('next')
                if next_url:
                    yield scrapy.Request(
                        url=next_url,
                        headers={"Accept": "*/*", "Content-Type": "application/json"},
                        meta={"release_date": release_date, "search_h": search_h},
                    )
            else:
                # Change search filter if count exceeds the API limit or search_h > 1 hour
                parts = int(ceil(count / self.api_limit))  # parts we split a search that exceeds the limit
                split_h = int(ceil(search_h / parts))  # hours we split

                # If we have last_hour variable here, we have to split hours
                last_hour = response.request.meta.get('last_hour')
                if last_hour:
                    date = datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%S")  # release_date with start hour
                else:
                    date = datetime.strptime(release_date, "%Y-%m-%d")  # else we have to split a day by day range
                    last_hour = date.strftime("%Y-%m-%d") + 'T23:59:59'  # last hour of a day

                # Create time lists depending on how many hours we split a search
                start_hour_list = [(date + timedelta(hours=h)
                                    ).strftime("%Y-%m-%dT%H:%M:%S") for h in range(0, search_h, split_h)]
                end_hour_list = [(date + timedelta(hours=h, minutes=59, seconds=59)
                                  ).strftime("%Y-%m-%dT%H:%M:%S") for h in
                                 range(split_h - 1, search_h, split_h)]

                # If parts is not a divisor of hours we split, append the last missing hour
                if len(start_hour_list) != len(end_hour_list):
                    end_hour_list.append(last_hour)

                self.logger.info('Changing filters, split in {}: {}.'.format(parts, response.request.url))
                for i in range(parts):
                    yield scrapy.Request(
                        url=self.base_page_url.format(
                            start_hour_list[i],
                            end_hour_list[i]
                        ),
                        headers={"Accept": "*/*", "Content-Type": "application/json"},
                        meta={"release_date": start_hour_list[i],  # release_date with star hour
                              "last_hour": end_hour_list[i],  # release_date with last hour
                              "search_h": split_h},  # new search range
                    )
        else:
            yield {
                'success': False,
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
