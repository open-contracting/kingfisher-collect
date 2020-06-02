import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class HondurasPortalReleases(LinksSpider):
    name = 'honduras_portal_releases'
    data_type = 'release_package'
    data_pointer = '/releasePackage'
    next_pointer = '/next'
    next_page_formatter = parameters('page')

    download_delay = 0.9

    def start_requests(self):
        url = 'http://www.contratacionesabiertas.gob.hn/api/v1/release/?format=json'
        yield scrapy.Request(url, meta={'kf_filename': 'page-1.json'})
