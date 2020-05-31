import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class UKContractsFinder(BaseSpider):
    """
    Spider arguments
      sample
        Download only 100 release packages.
    """
    name = 'uk_contracts_finder'
    base_url = 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=asc&page=%d'

    def start_requests(self):
        yield scrapy.Request(self.base_url % 1, meta={'kf_filename': 'page1.json'})

    @handle_error
    def parse(self, response):
        yield self.build_file_from_response(
            response,
            data_type='release_package_list_in_results',
            encoding='iso-8859-1'
        )

        if not self.sample and response.request.meta['kf_filename'] == 'page1.json':
            json_data = json.loads(response.text)
            last_page = json_data['maxPage']
            for page in range(1, last_page + 1):
                yield scrapy.Request(self.base_url % page, meta={'kf_filename': 'page%d.json' % page})
