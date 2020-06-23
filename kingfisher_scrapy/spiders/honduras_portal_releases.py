import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class HondurasPortalReleases(LinksSpider):
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
    next_pointer = '/next'
    next_page_formatter = staticmethod(parameters('page'))

    download_delay = 0.9

    def start_requests(self):
        url = 'http://www.contratacionesabiertas.gob.hn/api/v1/release/?format=json'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'})
