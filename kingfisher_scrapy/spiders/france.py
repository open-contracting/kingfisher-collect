import scrapy

from kingfisher_scrapy.base_spiders.big_file_spider import BigFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class France(BigFileSpider):
    """
    Domain
      France
    Swagger API documentation
      https://doc.data.gouv.fr/api/reference/
    """
    name = 'france'

    def start_requests(self):
        # A CKAN API JSON response.
        # Ministère de l'économie, des finances et de la relance
        # https://www.data.gouv.fr/fr/datasets/donnees-essentielles-de-la-commande-publique-fichiers-consolides/
        url = 'https://www.data.gouv.fr/api/1/datasets/donnees-essentielles-de-la-commande-publique-fichiers' \
              '-consolides/'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        for resource in data['resources']:
            description = resource['description']
            if description and 'ocds' in description.lower():
                yield self.build_request(resource['url'], formatter=components(-2))
