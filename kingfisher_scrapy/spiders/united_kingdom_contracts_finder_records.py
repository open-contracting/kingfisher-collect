from kingfisher_scrapy.spiders.united_kingdom_contracts_finder_base import UnitedKingdomContractsFinderBase


class UnitedKingdomContractsFinderRecords(UnitedKingdomContractsFinderBase):
    """
    Domain
      Contracts Finder
    API documentation
      https://www.contractsfinder.service.gov.uk/apidocumentation/home
    """
    name = 'united_kingdom_contracts_finder_records'

    # SimpleSpider
    data_type = 'record_package'

    # UnitedKingdomContractsFinderBase
    parse_data_callback = 'parse'
