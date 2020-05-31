import hashlib
import json
from urllib.parse import urlparse

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.util import handle_error


class Malta(ZipSpider):
    name = 'malta'
    data_type = 'record_package'

    def start_requests(self):
        yield scrapy.Request(
            'http://demowww.etenders.gov.mt/ocds/services/recordpackage/getrecordpackagelist',
            meta={'kf_filename': 'start_requests'},
            callback=self.parse_list
        )

    @handle_error
    def parse_list(self, response):
        url = 'http://demowww.etenders.gov.mt{}'
        json_data = json.loads(response.text)
        packages = json_data['packagesPerMonth']
        for package in packages:
            parsed = urlparse(package)
            path = parsed.path
            if path:
                yield scrapy.Request(
                    url.format(path),
                    meta={'kf_filename': hashlib.md5(path.encode('utf-8')).hexdigest() + '.json'}
                )
                if self.sample:
                    break
