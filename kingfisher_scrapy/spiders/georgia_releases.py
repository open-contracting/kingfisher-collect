import scrapy

from kingfisher_scrapy.base_spider import LinksSpider


class GeorgiaReleases(LinksSpider):
    name = 'georgia_releases'
    start_urls = ['https://odapi.spa.ge/api/releases.json']

    def start_requests(self):
        yield scrapy.Request(
            url='https://odapi.spa.ge/api/releases.json',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        yield from self.parse_next_link(response, 'release_package')
