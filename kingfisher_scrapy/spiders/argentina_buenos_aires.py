import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class ArgentinaBuenosAires(SimpleSpider):
    """
    Domain
      Ciudad de Buenos Aires
    API documentation
      https://data.buenosaires.gob.ar/acerca/ckan
    Bulk download documentation
      https://data.buenosaires.gob.ar/dataset/buenos-aires-compras/archivo/2a3d077c-71b6-4ba7-8924-f3e38cf1b8fc
    """
    name = 'argentina_buenos_aires'
    custom_settings = {
        'DOWNLOAD_FAIL_ON_DATALOSS': False,
    }
    download_timeout = 99999  # to avoid user timeout when downloading the file

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        # A CKAN API JSON response.
        url = 'https://data.buenosaires.gob.ar/api/3/action/package_show?id=buenos-aires-compras'
        yield scrapy.Request(url, meta={'file_name': 'package_show.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for resource in response.json()['result']['resources']:
            if resource['format'].upper() == 'JSON':
                # Presently, only one URL matches.
                yield self.build_request(resource['url'], formatter=components(-1))
