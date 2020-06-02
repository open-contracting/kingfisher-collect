import json
from datetime import datetime, timedelta
from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.exceptions import AuthenticationError
from kingfisher_scrapy.util import parameters


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
    default_from_date = '2011-01-01'
    download_delay = 1
    request_time_limit = 60  # in minutes
    reauthenticating = False  # flag for request a new token
    start_time = None

    base_page_url = 'https://api.openopps.com/api/ocds/?format=json&ordering=releasedate&page_size=1000&' \
                    'releasedate__gte={}&releasedate__lte={}'

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
            'https://api.openopps.com/api/api-token-auth/',
            method='POST',
            headers={"Accept": "*/*", "Content-Type": "application/json"},
            body=json.dumps({"username": self.username, "password": self.password}),
            # Send duplicate requests when we re-authenticate before the token expires
            dont_filter=True,
            # Flag request access token for middleware and initial authentication for callback function
            meta={'token_request': True, 'initial_authentication': True},
            callback=self.parse_access_token
        )

    def parse_access_token(self, response):
        if self.is_http_success(response):
            r = json.loads(response.text)
            token = r.get('token')
            if token:
                self.logger.info(f'New access token: {token}')
                self.access_token = 'JWT ' + token
                self.start_time = datetime.now()
                # If the request is initial authentication, start requests
                if response.request.meta.get('initial_authentication'):
                    return self.start_requests_pages()
                # For reauthenticating request, set to False and continue
                self.reauthenticating = False
            else:
                self.logger.error(
                    f'Authentication failed. Status code: {response.status}. {response.text}')
                raise AuthenticationError()
        else:
            self.logger.error(
                f'Authentication failed. Status code: {response.status}. {response.text}')
            raise AuthenticationError()

    def start_requests_pages(self):
        search_h = 24  # start splitting one day search

        # Case if we want to download a sample
        if self.sample:
            date = datetime(2011, 1, 1)
            yield from self.request_range_per_day(date, date, search_h)
        else:
            # Case if we have date range parameters
            if self.from_date and self.until_date:
                yield from self.request_range_per_day(self.from_date, self.until_date, search_h)
            else:
                # Use larger ranges for filters with less than (api_limit) search results
                release_date_gte_list = ['', '2009-01-01', '2010-01-01', '2010-07-01']
                release_date_lte_list = ['2008-12-31', '2009-12-31', '2010-06-30', '2010-12-31']

                for i in range(len(release_date_gte_list)):
                    yield self.request_range(release_date_gte_list[i], release_date_lte_list[i], search_h)

                # Use smaller ranges (day by day) for filters with more than (api_limit) search results
                for year in range(2011, datetime.now().year + 1):
                    start_date = datetime(year, 1, 1)
                    end_date = datetime(year, datetime.now().month, datetime.now().day) \
                        if year == datetime.now().year else datetime(year, 12, 31)
                    yield from self.request_range_per_day(start_date, end_date, search_h)

    def request_range(self, start_date, end_date, search_h):
        return self.build_request(
            self.base_page_url.format(start_date, end_date),
            formatter=parameters('releasedate__gte', 'releasedate__lte'),
            meta={
                'release_date': start_date,
                'search_h': search_h,
            },
            headers={'Accept': '*/*', 'Content-Type': 'application/json'}
        )

    def request_range_per_day(self, start_date, end_date, search_h):
        date_list = [(start_date + timedelta(days=d)).strftime("%Y-%m-%d")
                     for d in range((end_date - start_date).days + 1)]

        for date in date_list:
            yield self.request_range(date, date, search_h)

    def parse(self, response):
        if self.is_http_success(response):
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
                    yield self.build_file_from_response(data=all_data, data_type='release_package_list')
                    if self.sample:
                        return

                next_url = results.get('next')
                if next_url:
                    yield self.build_request(
                        next_url,
                        formatter=parameters('releasedate__gte', 'releasedate__lte', 'page'),
                        meta={
                            'release_date': release_date,
                            'search_h': search_h,
                        },
                        headers={'Accept': '*/*', 'Content-Type': 'application/json'}
                    )

                # Tells if we have to re-authenticate before the token expires
                time_diff = datetime.now() - self.start_time
                if not self.reauthenticating and time_diff.total_seconds() > self.request_time_limit * 60:
                    self.logger.info(f'Time_diff: {time_diff.total_seconds()}')
                    self.reauthenticating = True
                    yield scrapy.Request(
                        'https://api.openopps.com/api/api-token-auth/',
                        method='POST',
                        headers={"Accept": "*/*", "Content-Type": "application/json"},
                        body=json.dumps({"username": self.username, "password": self.password}),
                        dont_filter=True,
                        meta={'token_request': True, 'initial_authentication': False},
                        priority=100000,
                        callback=self.parse_access_token
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

                self.logger.info(f'Changing filters, split in {parts}: {response.request.url}.')
                for i in range(len(start_hour_list)):
                    yield self.build_request(
                        self.base_page_url.format(start_hour_list[i], end_hour_list[i]),
                        formatter=parameters('releasedate__gte', 'releasedate__lte'),
                        meta={
                            'release_date': start_hour_list[i],  # release_date with star hour
                            'last_hour': end_hour_list[i],  # release_date with last hour
                            'search_h': split_h,  # new search range
                        },
                        headers={'Accept': '*/*', 'Content-Type': 'application/json'}
                    )
        else:
            # Message for pages that exceed the 10,000 search results in the range of one hour
            # These are pages with status 500 and 'page=11' in the URL request
            if response.status == 500 and response.request.url.count("page=11"):
                self.logger.info(f'Status: {response.status}. Results exceeded in a range of one hour, we save the '
                                 f'first 10,000 data for: {response.request.url}')
            else:
                yield self.build_file_error_from_response(response)
