import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class UKContractsFinder(BaseSpider):
    name = 'uk_contracts_finder'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }
    base_url = 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=asc&page=%d'

    def start_requests(self):
        yield scrapy.Request(
            url=self.base_url % 1,
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):

        if response.status == 200:

            self.save_response_to_disk(response, response.request.meta['kf_filename'])
            yield {
                'success': True,
                'file_name': response.request.meta['kf_filename'],
                'data_type': 'release_package_list_in_results',
                'url': response.request.url,
                'encoding': 'ISO-8859-1',
            }

            if not self.is_sample() and response.request.meta['kf_filename'] == 'page1.json':
                json_data = json.loads(response.body_as_unicode())
                last_page = json_data['maxPage']
                for page in range(1, last_page + 1):
                    yield scrapy.Request(
                        url=self.base_url % page,
                        meta={'kf_filename': 'page%d.json' % page}
                    )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
