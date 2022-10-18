import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import components, handle_http_error, parameters


class UnitedKingdomContractsFinderBase(LinksSpider):
    # The API has unpredictable and undocumented "too many requests" logic.
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    # BaseSpider
    max_attempts = 5
    retry_http_codes = [403]

    # LinksSpider
    formatter = staticmethod(parameters('cursor'))

    # Local
    url_prefix = 'https://www.contractsfinder.service.gov.uk/Published/'
    # parse_data must be provided by subclasses.

    def start_requests(self):
        # page = 0 causes "Incorrect request [page must be a number greater than 0]".
        # size > 100 causes "Incorrect request [size must be a number greater than 0 and maximum is 100]".
        url = f'{self.url_prefix}Notices/OCDS/Search?order=desc&size=100'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_data)

    def get_retry_wait_time(self, response):
        # https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/1/GET-Published-OCDS-Record
        return 300
