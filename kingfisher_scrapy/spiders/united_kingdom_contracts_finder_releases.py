from kingfisher_scrapy.spiders.united_kingdom_contracts_finder_base import UnitedKingdomContractsFinderBase


class UnitedKingdomContractsFinderReleases(UnitedKingdomContractsFinderBase):
    """
    Domain
      Contracts Finder
    API documentation
      https://www.contractsfinder.service.gov.uk/apidocumentation/home
    """
    name = 'united_kingdom_contracts_finder_releases'

    # BaseSpider
    root_path = 'results.item'

    # SimpleSpider
    data_type = 'release_package'
