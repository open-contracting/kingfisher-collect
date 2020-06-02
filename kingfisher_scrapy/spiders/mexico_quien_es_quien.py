import json
from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class MexicoQuienEsQuien(BaseSpider):
    name = 'mexico_quien_es_quien'
    download_delay = 0.9

    def start_requests(self):
        yield scrapy.Request(
            'https://api.quienesquien.wiki/v2/sources',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        pattern = 'https://api.quienesquien.wiki/v2/contracts?limit={limit}&offset={offset}'
        limit = 1000

        count = json.loads(response.text)['data'][0]['collections']['contracts']['count']
        for offset in range(ceil(count / limit)):
            url = pattern.format(limit=limit, offset=offset * limit)
            yield self.build_request(url, formatter=parameters('offset'))
            if self.sample:
                break

    @handle_http_error
    def parse(self, response):
        data = json.loads(response.text)
        yield self.build_file_from_response(
            response,
            data=json.dumps(data['data']).encode(),
            data_type='record_package_list'
        )
