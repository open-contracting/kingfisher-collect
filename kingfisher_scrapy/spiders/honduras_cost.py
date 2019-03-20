import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class HondurasCoST(BaseSpider):
    name = 'honduras_cost'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        yield scrapy.Request(
            url='http://67.207.88.38:8080/sisocs/records',
            meta={'kf_filename': '2014-02.json'}
        )

    def parse(self, response):
        if response.status == 200:
            self.save_response_to_disk(response, response.request.meta['kf_filename'])
            yield {
                'success': True,
                'file_name': response.request.meta['kf_filename'],
                'data_type': 'record_package',
                'url': response.request.url,
            }

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
