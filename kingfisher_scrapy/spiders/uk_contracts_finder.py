import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class UKContractsFinder(BaseSpider):
    name = 'uk_contracts_finder'
    base_url = 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=asc&page=%d'

    def start_requests(self):
        yield scrapy.Request(
            url=self.base_url % 1,
            meta={'kf_filename': 'page1.json'}
        )

    def parse(self, response):

        if response.status == 200:

            yield self.save_response_to_disk(
                response,
                response.request.meta['kf_filename'],
                data_type='release_package_list_in_results',
                encoding='ISO-8859-1'
            )

            if not self.sample and response.request.meta['kf_filename'] == 'page1.json':
                json_data = json.loads(response.text)
                last_page = json_data['maxPage']
                for page in range(1, last_page + 1):
                    yield scrapy.Request(
                        url=self.base_url % page,
                        meta={'kf_filename': 'page%d.json' % page}
                    )
        else:
            yield self.build_file_error_from_response(response)
