import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class SouthAfricaNationalTreasuryAPI(LinksSpider):
    """
    Domain
      South Africa National Treasury
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2017-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    Swagger API documentation
      https://ocds-api.etenders.gov.za/swagger/index.html
    """
    name = 'south_africa_national_treasury_api'

    # BaseSpider
    date_format = 'date'
    date_required = True
    default_from_date = '2017-01-01'

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    formatter = staticmethod(parameters('PageNumber', 'dateFrom'))

    def start_requests(self):
        from_date = self.from_date.strftime(self.date_format)
        until_date = self.until_date.strftime(self.date_format)
        yield scrapy.Request('https://ocds-api.etenders.gov.za/api/OCDSReleases?PageNumber=1&PageSize=50&'
                             f'dateFrom={from_date}&dateTo={until_date}',
                             meta={'file_name': f'{from_date}.json'})
