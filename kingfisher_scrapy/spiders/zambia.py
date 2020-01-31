import json
from io import BytesIO
from zipfile import ZipFile

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class Zambia(BaseSpider):
    name = 'zambia'

    def start_requests(self):
        yield scrapy.Request(
            'https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackagelist',
            callback=self.parse_list
        )

    def parse_list(self, response):
        if response.status == 200:

            json_data = json.loads(response.body_as_unicode())
            files_urls = json_data['packagesPerMonth']

            if self.is_sample():
                files_urls = [files_urls[0]]

            for file_url in files_urls:
                yield scrapy.Request(
                    file_url,
                    meta={'kf_filename': '%s.json' % file_url[-16:].replace('/', '-')},
                )

        else:
            yield {
                'success': False,
                'file_name': 'list.json',
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }

    def parse(self, response):
        if response.status == 200:
            zip_files = ZipFile(BytesIO(response.body))
            for finfo in zip_files.infolist():
                data = zip_files.open(finfo.filename).read()
                yield self.save_data_to_disk(data, finfo.filename, data_type='record_package', url=response.request.url)

        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
