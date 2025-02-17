from kingfisher_scrapy.spiders.united_kingdom_contracts_finder_base import UnitedKingdomContractsFinderBase
from kingfisher_scrapy.util import components, handle_http_error


class UnitedKingdomContractsFinderRecords(UnitedKingdomContractsFinderBase):
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

    name = 'united_kingdom_contracts_finder_records'

    # BaseSpider
    skip_pluck = 'Already covered (see code for details)'  # united_kingdom_contracts_finder_releases

    # SimpleSpider
    data_type = 'record_package'

    @handle_http_error
    def parse_page(self, response):
        for release in response.json()['releases']:
            yield self.build_request(
                f'https://www.contractsfinder.service.gov.uk/Published/OCDS/Record/{release["ocid"]}',
                formatter=components(-1),
            )
        yield self.next_link(response, callback=self.parse_page)
