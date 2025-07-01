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
    result_count_pointer = '/total'
    use_page = True
    start_page = 1
    formatter = None
    limit = 10
    parse_list_callback = 'parse_items'

    # Local
    main_url = 'https://eprocurement.ppcc.gov.lr/ocds/record/'

    def start_requests(self):
        url, kwargs = self.url_builder(1, None, None)
        yield scrapy.Request(url, **kwargs, callback=self.parse_list)

    def url_builder(self, value, data, response):
        return f'{self.main_url}searchRecords.action', {
            'method': 'POST',
            'headers': {'Accept': 'application/json', 'Content-Type': 'application/json;charset=UTF-8'},
            'body': json.dumps({"page": value, "pagesize": 10, "sortField": "ocid", "sortDir": "asc"}),
            'meta': {'file_name': f'page-{value}.json'},
        }

    @handle_http_error
    def parse_items(self, response):
        data = response.json()
        for item in data['items']:
            yield self.build_request(f'{self.main_url}downloadRecord/{item["id"]}/COMPILED.action',
                                     formatter=components(-2))
