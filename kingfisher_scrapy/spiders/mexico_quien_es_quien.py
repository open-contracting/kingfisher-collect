import hashlib
import json
from math import ceil

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class MexicoQuienEsQuien(BaseSpider):
    """
    API documentation
      https://quienesquienapi.readthedocs.io/es/latest/
    Swagger API documentation
      https://api.quienesquien.wiki/v2/docs/
    Spider arguments
      sample
        Download a single record package with 10 records.
    """
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

    def parse_count(self, response):
        if response.status == 200:
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
        else:
            yield self.build_file_error_from_response(response)

    def parse(self, response):
        if response.status == 200:

            json_data = json.loads(response.text)
            yield self.build_file(
                json.dumps(json_data['data']).encode(),
                response.request.meta['kf_filename'],
                data_type='record_package_list',
                url=response.request.url
            )

        else:
            yield self.build_file_error_from_response(response)
