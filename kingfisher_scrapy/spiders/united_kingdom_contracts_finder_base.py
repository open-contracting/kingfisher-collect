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
    parse_list_callback = 'parse_page'
    total_pages_pointer = '/maxPage'

    # Local
    max_attempts = 5
    retry_code = 403
    url_prefix = 'https://www.contractsfinder.service.gov.uk/Published/'
    wait_time = 300
    # parse_data_callback must be provided by subclasses.

    def start_requests(self):
        # page = 0 causes "Incorrect request [page must be a number greater than 0]".
        # size > 100 causes "Incorrect request [size must be a number greater than 0 and maximum is 100]".
        url = f'{self.url_prefix}Notices/OCDS/Search?order=desc&size=100'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)

    def parse_page(self, response):
        if self.is_http_success(response):
            for result in response.json()['results']:
                for release in result['releases']:
                    yield self.build_request(f'{self.url_prefix}OCDS/Record/{release["ocid"]}',
                                             formatter=components(-1),
                                             callback=getattr(self, self.parse_data_callback))
        else:
            yield self.build_retry_request_or_file_error(response, self.wait_time, self.max_attempts,
                                                         response.status == self.retry_code)

    def parse(self, response, **kwargs):
        if self.is_http_success(response):
            yield from super().parse(response)
        else:
            yield self.build_retry_request_or_file_error(response, self.wait_time, self.max_attempts,
                                                         response.status == self.retry_code)
