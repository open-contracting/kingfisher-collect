import scrapy

from kingfisher_scrapy.base_spider import BaseSpider, LinksSpider


class MoldovaReleases(BaseSpider, LinksSpider):
    name = 'moldova_releases'

    def start_requests(self):
        yield scrapy.Request(
            url='http://ocds.mepps.openprocurement.io/api/releases.json',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        return self.parse_next_link(response, self.sample, self.save_response_to_disk,
                                    'release_package')
