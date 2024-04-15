import json

import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.util import handle_http_error


class MexicoPlataformaDigitalNacionalBase(IndexSpider):
    # BaseSpider
    root_path = 'data.item'

    # SimpleSpider
    data_type = 'release'

    # IndexSpider
    result_count_pointer = '/pagination/total'
    limit = '/pagination/pageSize'
    use_page = True
    start_page = 0
    formatter = None

    # Local
    url_prefix = 'https://api.plataformadigitalnacional.org/s6/api/v1/search?supplier_id='

    # publisher_id must be provided by subclasses.

    def start_requests(self):
        yield scrapy.Request(
            f'{self.url_prefix}{self.publisher_id}',
            method='POST',
            meta={'file_name': 'page-0.json'},
            callback=self.parse_list,
        )

    def url_builder(self, value, data, response):
        return f'{self.url_prefix}{self.publisher_id}', {
            'method': 'POST',
            'headers': {'Accept': 'application/json', 'Content-Type': 'application/json'},
            'body': json.dumps({'page': value, 'pageSize': 10}),
            'meta': {'file_name': f'page-{value}.json'},
    }
