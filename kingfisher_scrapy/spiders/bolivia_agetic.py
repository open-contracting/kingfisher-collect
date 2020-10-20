import json

import scrapy

from kingfisher_scrapy.base_spider import FlattenSpider
from kingfisher_scrapy.util import components, handle_http_error


class BoliviaAgetic(FlattenSpider):
    """
    Bulk download documentation
      https://datos.gob.bo/id/dataset/contrataciones-agetic-2019-estandar-ocp
    Spider arguments
      sample
        Downloads the first file in the downloads page.
    """
    name = 'bolivia_agetic'
    data_type = 'release_list'

    def start_requests(self):
        # A CKAN API JSON response.
        url = 'https://datos.gob.bo/api/3/action/package_show?id=contrataciones-agetic-2019-estandar-ocp'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = json.loads(response.text)
        for resource in data['result']['resources']:
            if 'ocds' in resource['description']:
                # Presently, only one URL matches.
                yield self.build_request(resource['url'], formatter=components(-1))

            if self.sample:
                break
