import hashlib
import json
import datetime

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class NepalPortal(BaseSpider):
    name = 'nepal_portal'
    custom_settings = {
        'ITEM_PIPELINES': {
            'kingfisher_scrapy.pipelines.KingfisherPostPipeline': 400
        },
        'HTTPERROR_ALLOW_ALL': True,
    }

    def start_requests(self):
        current_year = 2013
        if self.is_sample():
            end_year = 2013
        else:
            now = datetime.datetime.now()
            end_year = now.year

        while current_year <= end_year:
            url = 'http://ppip.gov.np/bulk-download/{}'.format(current_year)
            yield scrapy.Request(
                url,
                meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
            )
            current_year += 1

    def parse(self, response):
        if response.status == 200:
            json_data = json.loads(response.body_as_unicode())
            yield self.save_data_to_disk(
                json.dumps(json_data).encode(),
                response.request.meta['kf_filename'],
                data_type='release_package',
                url=response.request.url
            )

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
