import hashlib
import json
import scrapy
from kingfisher_scrapy.base_spider import BaseSpider


class KenyaMakueni(BaseSpider):
    name = 'kenya_makueni'
    download_delay = 0.9
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        if self.is_sample():
            url = 'https://opencontracting.makueni.go.ke/api/ocds/package/ocid/ocds-muq5cl-18757'
        else:
            url = 'https://opencontracting.makueni.go.ke/api/ocds/package/all'

        yield scrapy.Request(
            url,
            meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
        )

    def parse(self, response):
        if response.status == 200:
            if self.is_sample():
                data_type = 'release_package',
            else:
                data_type = 'release_package_list',

            json_data = json.loads(response.body_as_unicode())
            yield self.save_data_to_disk(
                json.dumps(json_data).encode(),
                response.request.meta['kf_filename'],
                data_type=data_type,
                url=response.request.url
            )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
