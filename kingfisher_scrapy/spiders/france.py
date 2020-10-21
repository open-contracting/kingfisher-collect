import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error, parameters


class France(SimpleSpider):
    """
    Swagger API documentation
      https://doc.data.gouv.fr/api/reference/
    """
    name = 'france'
    data_type = 'release_package'

    def start_requests(self):
        # A CKAN API JSON response.
        url = 'https://www.data.gouv.fr/api/1/datasets/?organization=534fff75a3a7292c64a77de4'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = json.loads(response.text)
        for item in data['data']:
            for resource in item['resources']:
                description = resource['description']
                if description and 'ocds' in description.lower():
                    yield self.build_request(resource['url'], formatter=components(-2))
            else:
                continue
        else:
            next_page = data.get('next_page')
            if next_page:
                yield self.build_request(next_page, formatter=parameters('page'), callback=self.parse_list)
