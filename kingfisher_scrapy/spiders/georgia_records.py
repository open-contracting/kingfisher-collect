import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class GeorgiaRecords(LinksSpider):
    name = 'georgia_records'
    data_type = 'record_package'
    next_page_formatter = parameters('page')

    def start_requests(self):
        url = 'https://odapi.spa.ge/api/records.json'
        yield scrapy.Request(url, meta={'kf_filename': 'page-1.json'})
