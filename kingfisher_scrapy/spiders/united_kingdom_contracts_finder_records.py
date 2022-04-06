import scrapy

from kingfisher_scrapy.spiders.united_kingdom_contracts_finder_base import \
    UnitedKingdomContractsFinderBase


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

    def parse(self, response):
        for result in response.json()['results']:
            for release in result['releases']:
                ocid = release["ocid"]
                url = f'https://www.contractsfinder.service.gov.uk/Published/OCDS/Record/{ocid}'
                yield scrapy.Request(url, meta={'file_name': f'{ocid}.json'}, callback=super().parse)

