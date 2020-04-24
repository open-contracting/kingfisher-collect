import json

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider


class Zambia(ZipSpider):
    name = 'zambia'

    def start_requests(self):
        yield scrapy.Request(
            'https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackagelist',
            callback=self.parse_list
        )

    def parse_list(self, response):
        if response.status == 200:

            json_data = json.loads(response.text)
            files_urls = json_data['packagesPerMonth']

            if self.sample:
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
        yield from self.parse_zipfile(response, data_type='record_package')
