import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class CanadaMontreal(BaseSpider):
    name = 'canada_montreal'
    page_limit = 10000

    def start_requests(self):
        yield scrapy.Request(
            url='https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit=%d' % self.page_limit,
            meta={'kf_filename': 'page0.json'}
        )

    @handle_error
    def parse(self, response):
        # Actual data
        yield self.build_file_from_response(
            response,
            response.request.meta['kf_filename'],
            data_type="release_package"
        )

        # Load more pages?
        if not self.sample and response.request.meta['kf_filename'] == 'page0.json':
            data = json.loads(response.text)
            total = data['meta']['count']
            offset = self.page_limit
            while offset < total:
                url = 'https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit=%d&offset=%d' % \
                      (self.page_limit, offset)
                yield scrapy.Request(
                    url=url,
                    meta={'kf_filename': 'page' + str(offset) + '.json'}
                )
                offset += self.page_limit
