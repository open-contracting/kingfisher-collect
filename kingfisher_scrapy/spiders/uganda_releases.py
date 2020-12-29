import json

import scrapy

from kingfisher_scrapy.base_spider import IndexSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters


class Uganda(IndexSpider):
    """
    Domain
      Government Procurement Portal (GPP) of Public Procurement and Disposal of Public Assets Authority (PPDA)
    API documentation
      https://docs.google.com/spreadsheets/d/10tVioy-VOQa1FwWoRl5e1pMbGpiymA0iycNcoDFkvks/edit#gid=365266172
    """
    name = 'uganda_releases'
    data_type = 'release_package'
    total_pages_pointer = '/data/last_page'
    yield_list_results = False
    formatter = staticmethod(parameters('page'))
    base_url = 'https://gpp.ppda.go.ug/adminapi/public/api/pdes'

    download_delay = 0.9

    def start_requests(self):
        yield scrapy.Request(
            'https://gpp.ppda.go.ug/adminapi/public/api/pdes',
            meta={'file_name': 'page-1.json'},
            callback=self.parse_list,
            cb_kwargs={'callback': self.parse_data}
        )

    @handle_http_error
    def parse_data(self, response):
        pattern = 'https://gpp.ppda.go.ug/adminapi/public/api/open-data/v1/releases/{}?fy={}&pde={}'

        data = response.json()
        for pdes in data['data']['data']:
            for plans in pdes['procurement_plans']:
                for tag in ('planning', 'tender', 'award', 'contract'):
                    yield self.build_request(
                        pattern.format(tag, plans['financial_year'], plans['pde_id']),
                        formatter=join(components(-1), parameters('fy', 'pde'))
                    )
