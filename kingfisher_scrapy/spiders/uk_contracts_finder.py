from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class UKContractsFinder(IndexSpider):
    """
    Domain
      Contracts Finder
    """
    name = 'uk_contracts_finder'

    # BaseSpider
    ocds_version = '1.0'  # uses deprecated fields
    root_path = 'results.item'

    # SimpleSpider
    data_type = 'release_package'

    # IndexSpider
    total_pages_pointer = '/maxPage'
    formatter = staticmethod(parameters('page'))

    def start_requests(self):
        url = 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=desc&page=1'
        yield self.build_request(url, formatter=parameters('page'), callback=self.parse_list)

    def parse(self, response, **kwargs):
        if self.is_http_success(response):
            yield from super().parse(response)
        else:
            request = response.request.copy()
            wait_time = int(response.headers.get('Retry-After', 1))
            request.meta['wait_time'] = wait_time
            request.dont_filter = True
            self.logger.info('Retrying %(request)s in %(wait_time)ds: HTTP %(status)d',
                             {'request': response.request, 'status': response.status,
                              'wait_time': wait_time}, extra={'spider': self})

            yield request
