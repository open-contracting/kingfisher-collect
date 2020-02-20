import scrapy

from kingfisher_scrapy.base_spider import LinksSpider


class MoldovaReleases(LinksSpider):
    name = 'moldova_releases'

    def start_requests(self):
        yield scrapy.Request(
            url='http://ocds.mepps.openprocurement.io/api/releases.json',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        yield from self.parse_next_link(response, 'release_package')
