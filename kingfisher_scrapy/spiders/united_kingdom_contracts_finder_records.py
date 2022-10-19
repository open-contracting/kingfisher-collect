from kingfisher_scrapy.spiders.united_kingdom_contracts_finder_base import UnitedKingdomContractsFinderBase
from kingfisher_scrapy.util import components, handle_http_error


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

    @handle_http_error
    def parse_data(self, response):
        for release in response.json()['releases']:
            yield self.build_request(f'{self.url_prefix}/OCDS/Record/{release["ocid"]}', formatter=components(-1))
