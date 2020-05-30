import scrapy

from kingfisher_scrapy.base_spider import LinksSpider


class Armenia(LinksSpider):
    name = 'armenia'
    data_type = 'release_package'
    next_pointer = '/next_page/uri'

    def start_requests(self):
        yield scrapy.Request('https://armeps.am/ocds/release', meta={'kf_filename': 'page1.json'})
