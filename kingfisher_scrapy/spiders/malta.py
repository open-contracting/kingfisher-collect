import hashlib
import json
from urllib.parse import urlparse

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider


class Malta(ZipSpider):
    """
    API documentation
      https://docs.google.com/document/d/1VnCEywKkkQ7BcVbT7HlW2s_N_QI8W0KE/edit
    Spider arguments
      sample
        Download only data released on October 2019.
    """
    name = 'malta'

    def start_requests(self):
        yield scrapy.Request(
            'http://demowww.etenders.gov.mt/ocds/services/recordpackage/getrecordpackagelist',
            meta={'kf_filename': 'start_requests'},
            callback=self.parse_list
        )

    def parse_list(self, response):
        if response.status == 200:
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
        else:
            yield {
                'success': False,
                'kf_filename': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }

    def parse(self, response):
        yield from self.parse_zipfile(response, data_type='record_package')
