from kingfisher_scrapy.spiders.united_kingdom_contracts_finder_base import UnitedKingdomContractsFinderBase
from kingfisher_scrapy.util import components


class UnitedKingdomContractsFinderReleases(UnitedKingdomContractsFinderBase):
    """
    Domain
      Contracts Finder
    API documentation
      https://www.contractsfinder.service.gov.uk/apidocumentation/home
    """
    name = 'united_kingdom_contracts_finder_releases'

    # SimpleSpider
    data_type = 'release_package'

    # IndexSpider
    parse_list_callback = 'build_urls'

    def parse_data(self, response):
        if self.is_http_success(response):
            for result in response.json()['records']:
                for release in result['releases']:
                    yield self.build_request(release['url'], formatter=components(-1), callback=super().parse)
        else:
            request = response.request.copy()
            wait_time = int(response.headers.get('Retry-After', 1))
            request.meta['wait_time'] = wait_time
            request.dont_filter = True
            self.logger.info('Retrying %(request)s in %(wait_time)ds: HTTP %(status)d',
                             {'request': response.request, 'status': response.status,
                              'wait_time': wait_time}, extra={'spider': self})

            yield request
