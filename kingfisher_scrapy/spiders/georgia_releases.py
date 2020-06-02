import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class GeorgiaReleases(LinksSpider):
    name = 'georgia_releases'
    data_type = 'release_package'
    next_page_formatter = parameters('page')

    def start_requests(self):
        url = 'https://odapi.spa.ge/api/releases.json'
        yield scrapy.Request(url, meta={'kf_filename': 'page-1.json'})
