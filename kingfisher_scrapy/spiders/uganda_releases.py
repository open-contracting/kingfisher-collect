import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters


class Uganda(SimpleSpider):
    name = 'uganda_releases'
    data_type = 'release_package'

    download_delay = 0.9

    def start_requests(self):
        yield scrapy.Request(
            'https://gpp.ppda.go.ug/adminapi/public/api/pdes',
            meta={'kf_filename': 'page-1.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        pattern = 'https://gpp.ppda.go.ug/adminapi/public/api/pdes?page={}'

        if self.sample:
            total = 1
        else:
            data = json.loads(response.text)
            total = data['data']['last_page']

        for page in range(2, total + 1):
            yield self.build_request(pattern.format(page), formatter=parameters('page'), callback=self.parse_data)

    @handle_http_error
    def parse_data(self, response):
        pattern = 'https://gpp.ppda.go.ug/adminapi/public/api/open-data/v1/releases/{}?fy={}&pde={}'

        data = json.loads(response.text)
        for pdes in data['data']['data']:
            for plans in pdes['procurement_plans']:
                for tag in ('planning', 'tender', 'award', 'contract'):
                    yield self.build_request(
                        pattern.format(tag, plans['financial_year'], plans['pde_id']),
                        formatter=join(components(-1), parameters('fy', 'pde'))
                    )
                    if self.sample:
                        break
                if self.sample:
                    break
