import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider


class UnitedKingdomContractsFinder(IndexSpider):
    """
    Domain
      Contracts Finder
    API documentation
      https://www.contractsfinder.service.gov.uk/apidocumentation/home
    """
    name = 'united_kingdom_contracts_finder'

    # BaseSpider
    ocds_version = '1.0'  # uses deprecated fields

    # SimpleSpider
    data_type = 'record_package'

    # IndexSpider
    total_pages_pointer = '/maxPage'

    def start_requests(self):
        # page = 0 causes "Incorrect request [page must be a number greater than 0]".
        # size > 100 causes "Incorrect request [size must be a number greater than 0 and maximum is 100]".
        url = 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=desc&size=100'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)

    def parse(self, response, **kwargs):
        if self.is_http_success(response):
            for result in response.json()['results']:
                for release in result['releases']:
                    ocid = release["ocid"]
                    url = f'https://www.contractsfinder.service.gov.uk/Published/OCDS/Record/{ocid}'
                    yield scrapy.Request(url, meta={'file_name': f'{ocid}.json'}, callback=super().parse)
        else:
            request = response.request.copy()
            wait_time = int(response.headers.get('Retry-After', 1))
            request.meta['wait_time'] = wait_time
            request.dont_filter = True
            self.logger.info('Retrying %(request)s in %(wait_time)ds: HTTP %(status)d',
                             {'request': response.request, 'status': response.status,
                              'wait_time': wait_time}, extra={'spider': self})

            yield request
