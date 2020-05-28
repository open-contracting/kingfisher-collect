import scrapy

from kingfisher_scrapy.base_spider import LinksSpider


class GeorgiaReleases(LinksSpider):
    name = 'georgia_releases'
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            url='https://odapi.spa.ge/api/releases.json',
            meta={'kf_filename': 'page1.json'}
        )
