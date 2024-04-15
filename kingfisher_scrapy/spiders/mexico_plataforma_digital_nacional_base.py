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
    limit = '/pagination/pageSize'
    result_count_pointer = '/pagination/total'
    start_page = 1
    use_page = True

    # Local
    base_url = 'https://api.plataformadigitalnacional.org/s6/api/v1/search?supplier_id={}'

    # publisher_id must be provided by subclasses.

    def start_requests(self):
        yield scrapy.Request(self.base_url.format(self.publisher_id), meta={'file_name': 'page-0.json'},
                             callback=self.parse_list, method='POST')

    @handle_http_error
    def parse_list(self, response):
        data = self.parse_list_loader(response)
        yield from self.parse(response)
        for value in self.range_generator(data, response):
            payload = json.dumps({'page': value, 'pageSize': 10})
            yield scrapy.Request(self.base_url.format(self.publisher_id), body=payload,
                                 meta={'file_name': f'page-{value}.json'}, method='POST',
                                 headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
