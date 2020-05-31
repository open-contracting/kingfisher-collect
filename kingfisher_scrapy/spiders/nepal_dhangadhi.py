import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_error


class NepalDhangadhi(SimpleSpider):
    name = 'nepal_dhangadhi'
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            'https://admin.ims.susasan.org/api/static-data/dhangadhi',
            meta={'kf_filename': 'list.json'},
            callback=self.parse_list,
        )

    @handle_error
    def parse_list(self, response):
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
