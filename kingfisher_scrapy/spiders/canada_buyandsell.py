import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class CanadaBuyAndSell(BaseSpider):
    name = "canada_buyandsell"

    def start_requests(self):
        yield scrapy.Request(
            url='https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
            meta={'kf_filename': '13-14.json'}
        )
        if self.sample:
            return
        yield scrapy.Request(
            url='https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-14-15.json',
            meta={'kf_filename': '14-15.json'}
        )
        yield scrapy.Request(
            url='https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-15-16.json',
            meta={'kf_filename': '15-16.json'}
        )
        yield scrapy.Request(
            url='https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-16-17.json',
            meta={'kf_filename': '16-17.json'}
        )

    @handle_error
    def parse(self, response):
        yield self.build_file_from_response(response, data_type='release_package')
