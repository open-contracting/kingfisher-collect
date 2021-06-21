import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class KadunaStateBudeshiReleases(SimpleSpider):
    """
    Domain
        Kaduna State
    Bulk download documentation
        https://www.budeshi.ng/kadppa/api
    """
    name = 'kaduna_state_releases'

    # SimpleSpider
    data_type = 'release_package'
    base_url = 'https://www.budeshi.ng/kadppa/api/'

    def start_requests(self):
        url = f'{self.base_url}project_list'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        types = ['planning', 'tender', 'award', 'contract']
        data = response.json()
        for item in data:
            id = item['id']
            for type in types:
                url = f'{self.base_url}releases/{id}/{type}'
                yield self.build_request(url, formatter=components(-2))
