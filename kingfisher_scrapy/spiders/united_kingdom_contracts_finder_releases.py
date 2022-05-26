from kingfisher_scrapy.spiders.united_kingdom_contracts_finder_base import UnitedKingdomContractsFinderBase
from kingfisher_scrapy.util import components


class UnitedKingdomContractsFinderReleases(UnitedKingdomContractsFinderBase):
    """
    Domain
      Contracts Finder
    Caveats
        The records endpoint is used to get the releases URLs for each ocid.
    API documentation
      https://www.contractsfinder.service.gov.uk/apidocumentation/home
    """
    name = 'united_kingdom_contracts_finder_releases'

    # SimpleSpider
    data_type = 'release_package'

    # UnitedKingdomContractsFinderBase
    parse_data_callback = 'parse_data'

    def parse_data(self, response):
        if self.is_http_success(response):
            for result in response.json()['records']:
                for release in result['releases']:
                    yield self.build_request(release['url'], formatter=components(-1))
        else:
            return self.build_retry_request_or_file_error(response)
