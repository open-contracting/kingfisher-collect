import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class UnitedKingdomContractsFinderBase(LinksSpider):
    # The API has unpredictable and undocumented "too many requests" logic.
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    # BaseSpider
    date_format = 'datetime'
    date_required = True
    default_from_date = '2014-01-01T00:00:00'
    max_attempts = 5
    retry_http_codes = [403]

    # LinksSpider
    formatter = staticmethod(parameters('cursor'))

    # Local
    url_prefix = 'https://www.contractsfinder.service.gov.uk/Published/'
    # parse_page must be provided by subclasses.

    def start_requests(self):
        # size > 100 causes "Incorrect request [size must be a number greater than 0 and maximum is 100]".
        url = f'{self.url_prefix}Notices/OCDS/Search?size=100'
        if self.from_date and self.until_date:
            from_date = self.from_date.strftime(self.date_format)
            until_date = self.until_date.strftime(self.date_format)
            url = f'{url}&publishedFrom={from_date}&publishedTo={until_date}'

        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_page)

    def get_retry_wait_time(self, response):
        # https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/1/GET-Published-OCDS-Record
        return 300
