import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class CanadaBuyAndSell(BaseSpider):
    name = "canada_buyandsell"
    start_urls = ['https://buyandsell.gc.ca']
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://buyandsell.gc.ca/cds/public/ocds/tpsgc-pwgsc_ocds_EF-FY-13-14.json',
            meta={'kf_filename': '13-14.json'}
        )
        if hasattr(self, 'sample') and self.sample == 'true':
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

    def parse(self, response):
        if response.status == 200:
            self.save_response_to_disk(response, response.request.meta['kf_filename'])
            yield {
                'success': True,
                'file_name': response.request.meta['kf_filename'],
                "data_type": "release_package",
                "url": response.request.url,
            }
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
