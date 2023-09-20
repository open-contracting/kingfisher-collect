from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import handle_http_error, parameters, transcode_bytes


class UnitedKingdomContractsFinderBase(LinksSpider):
    # The API has unpredictable and undocumented "too many requests" logic.
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    # BaseSpider
    date_format = 'datetime'
    default_from_date = '2014-01-01T00:00:00'
    encoding = 'iso-8859-1'
    max_attempts = 5
    retry_http_codes = [403]

    # LinksSpider
    formatter = staticmethod(parameters('cursor'))

    # Local
    url_prefix = 'https://www.contractsfinder.service.gov.uk/Published/'
    # parse_page must be provided by subclasses.

    def start_requests(self):
        # https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/1/GET-Published-Notice-OCDS-Search
        url = f'{self.url_prefix}Notices/OCDS/Search?limit=100'
        if self.from_date and self.until_date:
            from_date = self.from_date.strftime(self.date_format)
            until_date = self.until_date.strftime(self.date_format)
            url = f'{url}&publishedFrom={from_date}&publishedTo={until_date}'
        else:
            until_date = datetime.utcnow().strftime(self.date_format)
        yield scrapy.Request(url, meta={'file_name': f'{until_date}.json'},  # reverse chronological order
                             callback=self.parse_page)

    @handle_http_error
    def parse(self, response):
        # Remove non-iso-8859-1 characters.
        response = response.replace(body=transcode_bytes(response.body, self.encoding))
        yield from super().parse(response)

    def get_retry_wait_time(self, response):
        # https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/1/GET-Published-OCDS-Record
        return 300
