import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.util import components


class UnitedKingdomContractsFinderBase(IndexSpider):
    # The API has unpredictable and undocumented "too many requests" logic.
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    # BaseSpider
    ocds_version = '1.0'  # uses deprecated fields

    # IndexSpider
    parse_list_callback = 'build_urls'
    total_pages_pointer = '/maxPage'

    # Avoid conflict with IndexSpider's `base_url`.
    uk_base_url = 'https://www.contractsfinder.service.gov.uk'
    # parse_data_callback must be provided by subclasses.

    def start_requests(self):
        # page = 0 causes "Incorrect request [page must be a number greater than 0]".
        # size > 100 causes "Incorrect request [size must be a number greater than 0 and maximum is 100]".
        url = f'{self.uk_base_url}/Published/Notices/OCDS/Search?order=desc&size=100'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)

    def build_retry_request_or_file_error(self, response):
        if response.status == 403:
            request = response.request.copy()
            # https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/1/GET-Published-OCDS-Record
            wait_time = 300
            request.meta['wait_time'] = wait_time
            request.dont_filter = True
            self.logger.info('Retrying %(request)s in %(wait_time)ds: HTTP %(status)d',
                             {'request': response.request, 'status': response.status,
                              'wait_time': wait_time}, extra={'spider': self})

            return request
        else:
            return self.build_file_error_from_response(response)

    def build_urls(self, response):
        if self.is_http_success(response):
            for result in response.json()['results']:
                for release in result['releases']:
                    yield self.build_request(f'{self.uk_base_url}/Published/OCDS/Record/{release["ocid"]}',
                                             formatter=components(-1),
                                             callback=getattr(self, self.parse_data_callback))
        else:
            yield self.build_retry_request_or_file_error(response)

    def parse(self, response, **kwargs):
        if self.is_http_success(response):
            yield from super().parse(response)
        else:
            yield self.build_retry_request_or_file_error(response)
