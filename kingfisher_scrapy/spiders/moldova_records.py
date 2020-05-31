import scrapy

from kingfisher_scrapy.base_spider import LinksSpider


class MoldovaRecords(LinksSpider):
    name = 'moldova_records'
    data_type = 'record_package'

    def start_requests(self):
        yield scrapy.Request(
            'http://ocds.mepps.openprocurement.io/api/records.json',
            meta={'kf_filename': 'page1.json'}
        )
