import scrapy

from kingfisher_scrapy.base_spider import BaseSpider, LinksSpider


class GeorgiaRecords(BaseSpider, LinksSpider):
    name = 'georgia_records'
    start_urls = ['https://odapi.spa.ge/api/records.json']

    def start_requests(self):
        yield scrapy.Request(
            url='https://odapi.spa.ge/api/records.json',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        return self.parse_next_link(response, self.sample, self.save_response_to_disk, 'record_package')
