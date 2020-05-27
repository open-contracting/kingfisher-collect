import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class CanadaBuyAndSell(BaseSpider):
    name = "canada_buyandsell"
    start_urls = ['https://buyandsell.gc.ca']

    def start_requests(self):
        yield scrapy.Request(
            url='https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-16-17.json',
            meta={'kf_filename': '16-17.json'}
        )
        if self.sample or self.last:
            return
        yield scrapy.Request(
            url='https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-15-16.json',
            meta={'kf_filename': '15-16.json'}
        )
        yield scrapy.Request(
            url='https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-14-15.json',
            meta={'kf_filename': '14-15.json'}
        )
        yield scrapy.Request(
            url='https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
            meta={'kf_filename': '13-14.json'}
        )

    def parse(self, response):
        if response.status == 200:
            if self.last:
                yield self.build_last_release_date_item(response, 'releases')
            else:
                yield self.build_file_from_response(response, response.request.meta['kf_filename'],
                                                    data_type='release_package')
        else:
            yield self.build_file_error_from_response(response)
