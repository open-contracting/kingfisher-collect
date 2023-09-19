import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class SouthAfricaNationalTreasuryAPI(LinksSpider):
    """
    Domain
      South Africa National Treasury
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2021-05-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    Swagger API documentation
      https://ocds-api.etenders.gov.za/swagger/index.html
    """
    name = 'south_africa_national_treasury_api'

    # BaseSpider
    date_format = 'date'
    date_required = True
    default_from_date = '2021-05-01'

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    formatter = staticmethod(parameters('PageNumber', 'dateFrom', 'dateTo'))

    def start_requests(self):

        yield scrapy.Request('https://ocds-api.etenders.gov.za/api/OCDSReleases?PageNumber=1&PageSize=50&'
                             f'dateFrom={self.from_date}&dateTo={self.until_date}',
                             meta={'file_name': f'{self.from_date}-{self.until_date}-start.json'})
