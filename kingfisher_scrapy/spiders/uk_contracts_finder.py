from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class UKContractsFinder(IndexSpider):
    """
    Spider arguments
      sample
        Downloads the first page of release packages returned by the main endpoint.
    """
    name = 'uk_contracts_finder'
    data_type = 'release_package_list_in_results'
    encoding = 'iso-8859-1'
    formatter = staticmethod(parameters('page'))
    total_pages_pointer = '/maxPage'

    def start_requests(self):
        url = 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=desc&page=1'
        yield self.build_request(url, formatter=parameters('page'), callback=self.parse_list)
