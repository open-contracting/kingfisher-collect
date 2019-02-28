import json
import scrapy
import hashlib

from kingfisher_scrapy.base_spider import BaseSpider


class Armenia(BaseSpider):
    name = 'armenia'
    start_urls = ['https://armeps.am/ocds/release']
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://armeps.am/ocds/release',
            meta={'kf_filename': 'page1.json'}
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

            json_data = json.loads(response.body_as_unicode())
            if not (hasattr(self, 'sample') and self.sample == 'true'):
                if 'next_page' in json_data and 'uri' in json_data['next_page']:
                    url = json_data['next_page']['uri']
                    yield scrapy.Request(
                        url=url,
                        meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest()+'.json'}
                    )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
