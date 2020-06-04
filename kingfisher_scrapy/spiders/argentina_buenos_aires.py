import json

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.util import components, handle_http_error


class ArgentinaBuenosAires(ZipSpider):
    """
    Bulk download documentation
      https://data.buenosaires.gob.ar/dataset/buenos-aires-compras/archivo/2a3d077c-71b6-4ba7-8924-f3e38cf1b8fc
    API documentation
      https://data.buenosaires.gob.ar/acerca/ckan
    Spider arguments
      sample
        Downloads the zip file and sends 10 releases to kingfisher process.
    """
    name = 'argentina_buenos_aires'
    data_type = 'release_package'
    zip_file_format = 'release_package'

    # the data list service takes too long to be downloaded, so we increase the download timeout
    download_timeout = 1000

    def start_requests(self):
        # A CKAN API JSON response.
        url = 'https://data.buenosaires.gob.ar/api/3/action/package_show?id=buenos-aires-compras'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = json.loads(response.text)
        for resource in data['result']['resources']:
            if resource['format'].upper() == 'JSON':
                # Presently, only one URL matches.
                yield self.build_request(resource['url'], formatter=components(-1))
