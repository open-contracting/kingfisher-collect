from kingfisher_scrapy.base_spiders import LinksSpider, PeriodicSpider
from kingfisher_scrapy.util import handle_http_error, parameters, transcode_bytes


class UnitedKingdomContractsFinderReleases(LinksSpider, PeriodicSpider):
    """
    Domain
      Contracts Finder
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format). Defaults to '2014-01-01T00:00:00'.
      until_date
        Download only data until this time (YYYY-MM-DDThh:mm:ss format). Defaults to now.
    API documentation
      https://www.contractsfinder.service.gov.uk/apidocumentation/home
    """

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

    # PeriodicSpider
    formatter = staticmethod(parameters('publishedFrom', 'publishedTo'))
    next_link_formatter = staticmethod(parameters('publishedFrom', 'publishedTo', 'cursor'))
    step = 15
    pattern = (
        'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search'
        '?limit=100&publishedFrom={0:%Y-%m-%d}&publishedTo={1:%Y-%m-%d}'
    )

    name = 'united_kingdom_contracts_finder_releases'

    # SimpleSpider
    data_type = 'release_package'

    @handle_http_error
    def parse(self, response):
        # Remove non-iso-8859-1 characters.
        response = response.replace(body=transcode_bytes(response.body, self.encoding))
        yield from super().parse(response)

    def get_retry_wait_time(self, response):
        # https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/1/GET-Published-OCDS-Record
        return 300
