from kingfisher_scrapy.base_spiders import LinksSpider, PeriodicSpider
from kingfisher_scrapy.util import parameters


class SouthAfricaNationalTreasuryAPI(LinksSpider, PeriodicSpider):
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
    custom_settings = {
        # Reduce the number of concurrent requests to avoid multiple failures.
        'CONCURRENT_REQUESTS': 1,
    }

    # BaseSpider
    date_format = 'date'
    date_required = True
    default_from_date = '2017-01-01'

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    formatter = staticmethod(parameters('PageNumber', 'dateFrom'))

    # PeriodicSpider
    pattern = (
      "https://ocds-api.etenders.gov.za/api/OCDSReleases?dateFrom={0:%Y-%m-%d}&dateTo={1:%Y-%m-%d}&PageNumber=1"
    )
    step = 7
