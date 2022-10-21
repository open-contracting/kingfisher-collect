from kingfisher_scrapy.spiders.united_kingdom_contracts_finder_base import UnitedKingdomContractsFinderBase
from kingfisher_scrapy.util import handle_http_error


class UnitedKingdomContractsFinderReleases(UnitedKingdomContractsFinderBase):
    """
    Domain
      Contracts Finder
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format).
        If ``until_date`` is provided, defaults to '2014-01-01T00:00:00'.
      until_date
        Download only data until this time (YYYY-MM-DDThh:mm:ss format).
        If ``from_date`` is provided, defaults to now.
    API documentation
      https://www.contractsfinder.service.gov.uk/apidocumentation/home
    """
    name = 'united_kingdom_contracts_finder_releases'

    # SimpleSpider
    data_type = 'release_package'

    @handle_http_error
    def parse_page(self, response):
        return self.parse(response)
