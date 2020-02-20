import scrapy

from kingfisher_scrapy.base_spider import LinksSpider


class GeorgiaRecords(LinksSpider):
    name = 'georgia_records'
    start_urls = ['https://odapi.spa.ge/api/records.json']

    def start_requests(self):
        yield scrapy.Request(
            url='https://odapi.spa.ge/api/records.json',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        yield from self.parse_next_link(response, 'record_package')
