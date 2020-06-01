import hashlib
import json
from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class MexicoQuienEsQuien(BaseSpider):
    name = 'mexico_quien_es_quien'
    download_delay = 0.9
    url = 'https://api.quienesquien.wiki/v2/contracts?limit={}&offset={}'

    def start_requests(self):
        if self.sample:
            limit = 10
            offset = 0
            yield scrapy.Request(
                self.url.format(limit, offset),
                meta={'kf_filename': 'sample.json'}
            )
        else:
            yield scrapy.Request(
                'https://api.quienesquien.wiki/v2/sources',
                meta={'kf_filename': 'start_requests'},
                callback=self.parse_count
            )

    @handle_error
    def parse_count(self, response):
        limit = 1000
        json_data = json.loads(response.text)
        count_list = json_data['data']
        count = int(count_list[0]['collections']['contracts']['count'])

        for offset in range(ceil(count / limit)):
            yield scrapy.Request(
                self.url.format(limit, (offset * limit)),
                meta={'kf_filename': hashlib.md5((self.url +
                                                  str(offset)).encode('utf-8')).hexdigest() + '.json'}
            )

    @handle_error
    def parse(self, response):
        json_data = json.loads(response.text)
        yield self.build_file_from_response(
            response,
            data=json.dumps(json_data['data']).encode(),
            data_type='record_package_list'
        )
