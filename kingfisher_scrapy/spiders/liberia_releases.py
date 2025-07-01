import json

import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.util import components, handle_http_error


class LiberiaReleases(IndexSpider):
    """
    Domain
      Public Procurement and Concessions Commission (PPCC)
    Bulk download documentation
      https://eprocurement.ppcc.gov.lr/ocds/report/home.action#/record
    """

    name = 'liberia_releases'

    # SimpleSpider
    data_type = 'release_package'

    # IndexSpider
    base_url = 'https://eprocurement.ppcc.gov.lr/ocds/record/'
    result_count_pointer = '/total'
    use_page = True
    start_page = 2
    formatter = None
    limit = 10
    parse_list_callback = 'parse_items'

    # Local
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json;charset=UTF-8'}
    payload = {"page": 1, "pagesize": 10, "sortField": "ocid", "sortDir": "asc"}

    def start_requests(self):
        yield scrapy.Request(
            f'{self.base_url}searchRecords.action',
            headers=self.headers,
            method='POST',
            body=json.dumps(self.payload),
            meta={'file_name': 'page-1.json'},
            callback=self.parse_list,
        )

    def url_builder(self, value, data, response):
        self.payload['page'] = value
        return f'{self.base_url}searchRecords.action', {
            'method': 'POST',
            'headers': self.headers,
            'body': json.dumps(self.payload),
            'meta': {'file_name': f'page-{value}.json'},
        }

    @handle_http_error
    def parse_items(self, response):
        data = response.json()
        for item in data['items']:
            yield self.build_request(f'{self.base_url}downloadRecord/{item["id"]}/COMPILED.action',
                                     formatter=components(-2))
