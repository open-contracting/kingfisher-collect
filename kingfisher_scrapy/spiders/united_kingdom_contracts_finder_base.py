import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.util import components, handle_http_error


class UnitedKingdomContractsFinderBase(IndexSpider):
    # The API has unpredictable and undocumented "too many requests" logic.
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    # BaseSpider
    ocds_version = '1.0'  # uses deprecated fields
    max_attempts = 5
    retry_http_codes = [403]

    # IndexSpider
    parse_list_callback = 'parse_page'
    page_count_pointer = '/maxPage'

    # Local
    url_prefix = 'https://www.contractsfinder.service.gov.uk/Published/'
    # parse_data_callback must be provided by subclasses.

    def start_requests(self):
        # page = 0 causes "Incorrect request [page must be a number greater than 0]".
        # size > 100 causes "Incorrect request [size must be a number greater than 0 and maximum is 100]".
        url = f'{self.url_prefix}Notices/OCDS/Search?order=desc&size=100'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_page(self, response):
        for result in response.json()['results']:
            for release in result['releases']:
                yield self.build_request(f'{self.url_prefix}OCDS/Record/{release["ocid"]}',
                                         formatter=components(-1), callback=getattr(self, self.parse_data_callback))

    def get_retry_wait_time(self, response):
        # https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/1/GET-Published-OCDS-Record
        return 300
