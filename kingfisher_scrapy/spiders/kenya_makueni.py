import hashlib
import json
import requests
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class KenyaMakueni(BaseSpider):
    name = 'kenya_makueni'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        if self.is_sample():
            page_size = 10
        else:
            count = requests.get('https://opencontracting.makueni.go.ke/api/ocds/release/count')
            page_size = int(count.text)

        if page_size > 300:
            url = 'https://opencontracting.makueni.go.ke/api/ocds/package/all?pageNumber={}'
            for page in range(page_size):
                yield scrapy.Request(
                    url.format(page),
                    meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
                )

        else:
            url = 'https://opencontracting.makueni.go.ke/api/ocds/package/all?pageSize={}'
            yield scrapy.Request(
                url.format(page_size),
                meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
            )

    def parse(self, response):
        if response.status == 200:
            json_data = json.loads(response.body_as_unicode())
            yield self.save_data_to_disk(
                json.dumps(json_data).encode(),
                response.request.meta['kf_filename'],
                data_type='release_package_list',
                url=response.request.url
            )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
