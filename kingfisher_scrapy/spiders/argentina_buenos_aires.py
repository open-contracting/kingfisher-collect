import json

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider


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
    start_urls = ['https://data.buenosaires.gob.ar/api/3/action/package_show?id=buenos-aires-compras']
    # the data list service takes too long to be downloaded, so we increase the download timeout
    download_timeout = 1000

    def start_requests(self):
        yield scrapy.Request(
            url='https://data.buenosaires.gob.ar/api/3/action/package_show?id=buenos-aires-compras',
            callback=self.parse_list
        )

    def parse_list(self, response):
        if response.status == 200:
            data = json.loads(response.text)
            for resource in data['result']['resources']:
                if resource['format'].upper() == 'JSON':
                    yield scrapy.Request(url=resource['url'])
        else:
            yield self.build_file_error_from_response(response, filename='list.json')

    def parse(self, response):
        yield from self.parse_zipfile(response, 'release_package', file_format='release_package')
