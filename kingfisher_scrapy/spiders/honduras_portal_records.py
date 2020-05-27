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
        yield scrapy.Request(
            url,
            meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
        )

    @handle_error()
    def parse(self, response):
        json_data = json.loads(response.text)
        yield self.build_file(
            json.dumps(json_data['releasePackage']).encode(),
            response.request.meta['kf_filename'],
            data_type='record_package',
            url=response.request.url
        )

        url = json_data.get('next')
        if not url or self.sample:
            return
        else:
            yield scrapy.Request(
                url,
                meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
            )
