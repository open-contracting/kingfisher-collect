import hashlib
import json
import scrapy
from kingfisher_scrapy.base_spider import BaseSpider


class HondurasPortalReleases(BaseSpider):
    name = 'honduras_portal_releases'
    download_delay = 0.9
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        url = 'http://200.13.162.86/api/v1/release/?format=json'
        yield scrapy.Request(
            url,
            meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
        )

    def parse(self, response):
        if response.status == 200:

            json_data = json.loads(response.body_as_unicode())
            yield self.save_data_to_disk(
                json.dumps(json_data.get('results')).encode(),
                response.request.meta['kf_filename'],
                data_type='release_list',
                url=response.request.url
            )

            url = json_data.get('next')
            if not url or self.is_sample():
                return
            else:
                yield scrapy.Request(
                    url,
                    meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
                )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
