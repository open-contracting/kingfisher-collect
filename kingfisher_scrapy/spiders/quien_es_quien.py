import hashlib
import json
import math
import requests

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class QuienEsQuienWiki(BaseSpider):
    name = 'quien_es_quien_wiki'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        if self.is_sample():
            url = 'https://api.quienesquien.wiki/v2/contracts?limit=10'
            yield scrapy.Request(
                url,
                meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
            )
        else:
            url = 'https://api.quienesquien.wiki/v2/contracts?limit=1000&offset={}'
            count = requests.get('https://api.quienesquien.wiki/v2/sources')
            dict = count.json()['data'][0]['collections']['contracts']['count']

            for offset in range(math.ceil(dict/1000)):
                yield scrapy.Request(
                    url.format(offset * 1000),
                    meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + str(offset) + '.json'}
                )

    def parse(self, response):
        if response.status == 200:

            json_data = json.loads(response.body_as_unicode())
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
