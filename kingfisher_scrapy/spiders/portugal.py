import json

import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class Portugal(CompressedFileSpider):
    """
    Domain
      Instituto dos Mercados Públicos, do Imobiliário e da Construção (IMPIC)
    API documentation
      https://dados.gov.pt/pt/apidoc/
    Swagger API documentation
      https://dados.gov.pt/pt/apidoc/#/datasets
    """
    name = 'portugal'
    data_type = 'record_package'
    encoding = 'iso-8859-1'
    compressed_file_format = 'json_lines'

    download_timeout = 9999

    def start_requests(self):
        # A CKAN API JSON response.
        url = 'https://dados.gov.pt/api/1/datasets/?q=ocds&organization=5ae97fa2c8d8c915d5faa3bf&page_size=20'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        for item in data['data']:
            for resource in item['resources']:
                description = resource['description']
                if description and 'ocds' in description.lower():
                    # Presently, only one URL matches.
                    yield self.build_request(resource['url'], formatter=components(-2))
