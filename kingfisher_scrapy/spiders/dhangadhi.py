import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class Dhangadhi(BaseSpider):
    name = "dhangadhi"
    start_urls = ['https://ims.susasan.org/dhangadhi#downloads']

    def start_requests(self):
        yield scrapy.Request(
            url='https://admin.ims.susasan.org/ocds/json/dhangadhi-2074-75.json',
            meta={'kf_filename': 'dhangadhi-2074-75.json'}
        )
        if not self.is_sample():
            yield scrapy.Request(
                url='https://admin.ims.susasan.org/ocds/json/dhangadhi-2075-76.json',
                meta={'kf_filename': 'dhangadhi-2075-76.json'}
            )

    def parse(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type="release_package")
        else:

            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
