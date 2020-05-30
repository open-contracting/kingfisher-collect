import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class Armenia(BaseSpider):
    name = 'armenia'

    def start_requests(self):
        yield scrapy.Request('https://armeps.am/ocds/release', meta={'kf_filename': 'page1.json'})

    @handle_error
    def parse(self, response):
        yield self.build_file_from_response(response, data_type='release_package')

        json_data = json.loads(response.text)
        if not (self.sample):
            if 'next_page' in json_data and 'uri' in json_data['next_page']:
                url = json_data['next_page']['uri']
                yield scrapy.Request(url, meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest()+'.json'})
