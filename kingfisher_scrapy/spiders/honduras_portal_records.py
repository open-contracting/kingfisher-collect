import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class HondurasPortalRecords(LinksSpider):
    name = 'honduras_portal_records'
    data_type = 'record_package'
    data_pointer = '/recordPackage'
    next_pointer = '/next'
    next_page_formatter = staticmethod(parameters('page'))

    download_delay = 0.9

    def start_requests(self):
        url = 'http://www.contratacionesabiertas.gob.hn/api/v1/record/?format=json'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'})
