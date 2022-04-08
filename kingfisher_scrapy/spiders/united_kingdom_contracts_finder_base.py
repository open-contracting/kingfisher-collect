import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.util import components


class UnitedKingdomContractsFinderBase(IndexSpider):
    uk_base_url = 'https://www.contractsfinder.service.gov.uk'
    # BaseSpider
    ocds_version = '1.0'  # uses deprecated fields

    # IndexSpider
    parse_list_callback = 'build_urls'
    total_pages_pointer = '/maxPage'

    def start_requests(self):
        # page = 0 causes "Incorrect request [page must be a number greater than 0]".
        # size > 100 causes "Incorrect request [size must be a number greater than 0 and maximum is 100]".
        url = f'{self.uk_base_url}/Published/Notices/OCDS/Search?order=desc&size=100'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)

    def build_retry_request(self, response):
        request = response.request.copy()
        wait_time = int(response.headers.get('Retry-After', 1))
        request.meta['wait_time'] = wait_time
        request.dont_filter = True
        self.logger.info('Retrying %(request)s in %(wait_time)ds: HTTP %(status)d',
                         {'request': response.request, 'status': response.status,
                          'wait_time': wait_time}, extra={'spider': self})

        return request

    def build_urls(self, response):
        if self.is_http_success(response):
            for result in response.json()['results']:
                for release in result['releases']:
                    yield self.build_request(f'{self.uk_base_url}/Published/OCDS/Record/{release["ocid"]}',
                                             formatter=components(-1),
                                             callback=getattr(self, self.parse_data_callback))
        else:
            yield self.build_retry_request(response)

    def parse(self, response, **kwargs):
        if self.is_http_success(response):
            yield from super().parse(response)
        else:
            yield self.build_retry_request(response)
