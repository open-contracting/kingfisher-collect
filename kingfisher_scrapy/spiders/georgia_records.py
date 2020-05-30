import scrapy

from kingfisher_scrapy.base_spider import LinksSpider


class GeorgiaRecords(LinksSpider):
    name = 'georgia_records'
    data_type = 'record_package'

    def start_requests(self):
        yield scrapy.Request('https://odapi.spa.ge/api/records.json', meta={'kf_filename': 'page1.json'})
