import json

import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import handle_http_error, components


class CostaRicaPoderJudicialReleases(CompressedFileSpider):
    """
    API documentation
      https://docs.ckan.org/en/2.8/api/
    Bulk download documentation
      http://datosabiertospj.eastus.cloudapp.azure.com/dataset/estandar-de-datos-de-contrataciones-abiertas-ocds
    Spider arguments
      sample
        Downloads the zip file and sends 10 releases to kingfisher process.
    """
    name = 'costa_rica_poder_judicial_releases'
    data_type = 'release_package'
    """ 
    ZIP file contains records and releases 
    the releases contains a "-" in their names so we use that character to filter them
    """
    file_name_must_contain = '-'

    def start_requests(self):
        url = 'http://datosabiertospj.eastus.cloudapp.azure.com/api/3/action/package_show?id=estandar-de-datos-de-contrataciones-abiertas-ocds'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = json.loads(response.text)
        for resource in data['result']['resources']:
            if resource['format'].upper() == 'ZIP':
                # Presently, only one URL matches.
                yield self.build_request(resource['url'], formatter=components(-1))
                if self.sample:
                    return
