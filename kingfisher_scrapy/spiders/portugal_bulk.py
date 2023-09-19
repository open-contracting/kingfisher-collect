import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class PortugalBulk(CompressedFileSpider):
    """
    Domain
      Instituto dos Mercados Públicos, do Imobiliário e da Construção (IMPIC)
    API documentation
      https://dados.gov.pt/pt/apidoc/
    Bulk download documentation
      https://dados.gov.pt/pt/datasets/ocds-portal-base-www-base-gov-pt/
    Swagger API documentation
      https://dados.gov.pt/pt/apidoc/#/datasets
    """
    name = 'portugal_bulk'
    download_timeout = 9999

    # BaseSpider
    line_delimited = True
    skip_pluck = 'Already covered (see code for details)'  # portugal_releases

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        # A CKAN API JSON response.
        url = 'https://dados.gov.pt/api/1/datasets/?q=ocds&organization=5ae97fa2c8d8c915d5faa3bf&page_size=20'
        yield scrapy.Request(url, meta={'file_name': 'package_search.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        # Presently, only one URL matches:
        # https://dados.gov.pt/s/resources/ocds-portal-base-www-base-gov-pt/20210415-224406/base2-pt-ocds-202004.zip
        for item in response.json()['data']:
            for resource in item['resources']:
                description = resource['description']
                if description and 'ocds' in description.lower():
                    yield self.build_request(resource['url'], formatter=components(-2))
