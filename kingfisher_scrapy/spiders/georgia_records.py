import scrapy

from kingfisher_scrapy.base_spider import BaseSpider, LinksSpider


class GeorgiaRecords(BaseSpider, LinksSpider):
    name = 'georgia_records'
    start_urls = ['https://odapi.spa.ge/api/records.json']

    def start_requests(self):
        yield scrapy.Request(
            url='https://odapi.spa.ge/api/records.json',
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):
        if response.status == 200:

            yield self.save_response_to_disk(response, response.request.meta['kf_filename'], data_type="record_package")

            if not self.sample:
                yield self.next_link(response)
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
