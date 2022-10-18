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

    def parse_data(self, response):
        for release in response.json()['releases']:
            yield self.build_request(f'{self.url_prefix}/OCDS/Release/{release["id"]}', formatter=components(-1))

