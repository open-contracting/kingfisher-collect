import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class NepalDhangadhi(BaseSpider):
    name = "nepal_dhangadhi"

    def start_requests(self):
        yield scrapy.Request(
            'https://admin.ims.susasan.org/api/static-data/dhangadhi',
            callback=self.parse_item,
        )

    @handle_error()
    def parse_item(self, response):
        url = 'https://admin.ims.susasan.org/ocds/json/dhangadhi-{}.json'
        json_data = json.loads(response.text)
        fiscal_years = json_data['data']['fiscal_years']
        for item in fiscal_years:
            fy = item['name']
            yield scrapy.Request(
                url.format(fy),
                meta={'kf_filename': hashlib.md5((url + fy).encode('utf-8')).hexdigest() + '.json'},
            )
            if self.sample:
                break

    @handle_error()
    def parse(self, response):
        yield self.build_file_from_response(
            response,
            response.request.meta['kf_filename'],
            data_type='release_package'
        )
