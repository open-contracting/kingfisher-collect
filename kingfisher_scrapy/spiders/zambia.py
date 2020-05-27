import json

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.util import handle_error


class Zambia(ZipSpider):
    name = 'zambia'

    def start_requests(self):
        yield scrapy.Request(
            'https://www.zppa.org.zm/ocds/services/recordpackage/getrecordpackagelist',
            meta={'kf_filename': 'list.json'},
            callback=self.parse_list
        )

    @handle_error
    def parse_list(self, response):
        json_data = json.loads(response.text)
        files_urls = json_data['packagesPerMonth']

        if self.sample:
            files_urls = [files_urls[0]]

        for file_url in files_urls:
            yield scrapy.Request(
                file_url,
                meta={'kf_filename': '%s.json' % file_url[-16:].replace('/', '-')},
            )

    @handle_error
    def parse(self, response):
        yield from self.parse_zipfile(response, data_type='record_package')
