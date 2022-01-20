import scrapy

from kingfisher_scrapy.base_spiders.simple_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class ItalyAppaltiPOP(SimpleSpider):
    """
    Domain
      AppaltiPOP
    Bulk download documentation
      https://www.appaltipop.it/it/download
    Swagger API documentation
      https://www.appaltipop.it/api/v1/
    """
    name = 'italy_appalti_pop'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            'https://www.appaltipop.it/api/v1/buyers',
            meta={'file_name': 'buyers.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        # The data looks like:
        # {
        #   "total": { ... },
        #   max_score: ...,
        #   hits: [ ... ]
        # }

        for buyer in data['hits']:
            # The first resource in the list is the OCDS JSON, the second one a XLSX file
            resource = buyer['_source']['appaltipop:releases/0/buyer/dataSource/resources'][0]

            # The JSON file path looks like 'data/IT-CF-01232710374/ocds.json'
            file_path = resource['appaltipop:releases/0/buyer/resource/url']
            url = f'https://raw.githubusercontent.com/ondata/appaltipop/master/{file_path}'
            yield self.build_request(url, formatter=components(-2))
