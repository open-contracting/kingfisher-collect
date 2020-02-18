import datetime
import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class NepalPortal(BaseSpider):
    name = 'nepal_portal'

    def start_requests(self):
        if self.sample:
            current_year = 2018
            end_year = 2018
        else:
            current_year = 2013
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
