import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class HondurasPortalRecords(BaseSpider):
    name = 'honduras_portal_records'
    download_delay = 0.9

    def start_requests(self):
        url = 'http://www.contratacionesabiertas.gob.hn/api/v1/record/?format=json'
        yield scrapy.Request(url, meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'})

    @handle_error
    def parse(self, response):
        json_data = json.loads(response.text)
        yield self.build_file_from_response(
            response,
            data=json.dumps(json_data['releasePackage']).encode(),
            data_type='record_package'
        )

        url = json_data.get('next')
        if url and not self.sample:
            yield scrapy.Request(url, meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'})
