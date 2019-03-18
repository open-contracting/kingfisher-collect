import json

import datetime
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class IndonesiaBandung(BaseSpider):
    name = 'indonesia_bandung'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }
    base_url = 'https://birms.bandung.go.id/api/packages/year/{}?page={}'

    def start_requests(self):
        yield scrapy.Request(
            url=self.base_url.format(2013, 1),
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

            if not self.is_sample() and response.request.meta['kf_filename'] == 'page1.json':
                json_data = json.loads(response.body_as_unicode())
                current_year = datetime.datetime.now().year + 1
                for year in range(2013, current_year):
                    last_page = json_data['last_page']
                    for page in range(1, last_page + 1):
                        yield scrapy.Request(
                            url=self.base_url.format(year, page),
                            meta={'kf_filename': 'year{}page{}.json'.format(year, page)}
                        )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
