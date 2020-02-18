import scrapy

from kingfisher_scrapy.base_spider import BaseSpider, LinksSpider


class MoldovaRecords(BaseSpider, LinksSpider):
    name = 'moldova_records'

    def start_requests(self):
        yield scrapy.Request(
            url='http://ocds.mepps.openprocurement.io/api/records.json',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        yield self.parse_next_link(response, self.sample, self.save_response_to_disk, 'record_package')
