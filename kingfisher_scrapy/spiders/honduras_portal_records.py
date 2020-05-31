import hashlib

import scrapy

from kingfisher_scrapy.base_spider import LinksSpider


class HondurasPortalRecords(LinksSpider):
    """
    API documentation
      http://www.contratacionesabiertas.gob.hn/servicio/
    Spider arguments
      sample
        Download only the first record package in the dataset.
    """
    name = 'honduras_portal_records'
    data_type = 'record_package'
    data_pointer = '/recordPackage'
    next_pointer = '/next'

    download_delay = 0.9

    def start_requests(self):
        url = 'http://www.contratacionesabiertas.gob.hn/api/v1/record/?format=json'
        yield scrapy.Request(url, meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'})
