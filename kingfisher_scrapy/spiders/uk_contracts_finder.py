from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class UKContractsFinder(IndexSpider):
    """
    Domain
      Contracts Finder
    """
    name = 'uk_contracts_finder'
    data_type = 'release_package'
    encoding = 'iso-8859-1'
    formatter = staticmethod(parameters('page'))
    total_pages_pointer = '/maxPage'
    root_path = 'results.item'

    def start_requests(self):
        url = 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=desc&page=1'
        yield self.build_request(url, formatter=parameters('page'), callback=self.parse_list)
