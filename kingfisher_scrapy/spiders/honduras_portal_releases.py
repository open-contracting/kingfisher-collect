import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import parameters


class HondurasPortalReleases(IndexSpider):
    """
    API documentation
      http://www.contratacionesabiertas.gob.hn/manual_api/
    Swagger API documentation
      http://www.contratacionesabiertas.gob.hn/servicio/
    Spider arguments
      sample
        Download only the first release package in the dataset.
    """
    name = 'honduras_portal_releases'
    data_type = 'release_package'
    data_pointer = '/releasePackage'
    total_pages_pointer = '/pages'
    formatter = staticmethod(parameters('page'))

    download_delay = 0.9

    def start_requests(self):
        yield scrapy.Request('http://www.contratacionesabiertas.gob.hn/api/v1/release/?format=json',
                             meta={'file_name': 'page-1.json'}, callback=self.parse_list)
