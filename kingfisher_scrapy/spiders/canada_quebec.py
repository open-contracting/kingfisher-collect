import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class CanadaQuebec(SimpleSpider):
    """
    Domain
      Secrétariat du Conseil du trésor
    Bulk download documentation
      https://www.donneesquebec.ca/recherche/dataset/systeme-electronique-dappel-doffres-seao
    """
    name = 'canada_quebec'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        # A CKAN API JSON response.
        url = 'https://www.donneesquebec.ca/api/3/action/package_show?id=d23b2e02-085d-43e5-9e6e-e1d558ebfdd5'
        yield scrapy.Request(url, meta={'file_name': 'package_show.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for resource in response.json()['result']['resources']:
            if resource['format'].upper() == 'JSON':
                yield self.build_request(resource['url'], formatter=components(-1))
