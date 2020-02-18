import hashlib
import json
from math import ceil

import requests
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class QuienEsQuien(BaseSpider):
    name = 'quien_es_quien'
    download_delay = 0.9

    def start_requests(self):
        if self.sample:
            limit = 10
            url = 'https://api.quienesquien.wiki/v2/contracts?limit={}'
            yield scrapy.Request(
                url.format(limit),
                meta={'kf_filename': 'sample.json'}
            )
        else:
            limit = 1000
            url = 'https://api.quienesquien.wiki/v2/contracts?limit={}&offset={}'
            count = requests.get('https://api.quienesquien.wiki/v2/sources')
            dict = count.json()['data'][0]['collections']['contracts']['count']

            for offset in range(ceil(dict/limit)):
                yield scrapy.Request(
                    url.format(limit, (offset * limit)),
                    meta={'kf_filename': hashlib.md5((url + str(offset)).encode('utf-8')).hexdigest() + '.json'}
                )

    def parse(self, response):
        if response.status == 200:

            json_data = json.loads(response.text)
            yield self.save_data_to_disk(
                json.dumps(json_data.get('data')).encode(),
                response.request.meta['kf_filename'],
                data_type='record_package_list',
                url=response.request.url
            )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
