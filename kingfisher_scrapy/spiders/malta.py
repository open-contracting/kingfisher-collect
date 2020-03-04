import hashlib
import json
from io import BytesIO
from urllib.parse import urlparse
from zipfile import ZipFile

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class Malta(BaseSpider):
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
            packages = json_data.get('packagesPerMonth')
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
        if response.status == 200:
            zip_file = ZipFile(BytesIO(response.body))
            for finfo in zip_file.infolist():
                data = zip_file.open(finfo.filename).read()
                yield self.save_data_to_disk(
                    data,
                    response.request.meta['kf_filename'] + finfo.filename,
                    data_type='record_package',
                    url=response.request.url
                )
        else:
            yield {
                'success': False,
                'kf_filename': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
