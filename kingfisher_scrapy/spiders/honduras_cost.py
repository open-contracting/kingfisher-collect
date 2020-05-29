import hashlib

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class HondurasCoST(BaseSpider):
    name = 'honduras_cost'

    def start_requests(self):
        yield scrapy.Request(
            'http://app.sisocs.org/protected/ocdsShow/',
            meta={'kf_filename': 'list.html'},
        )

    @handle_error
    def parse(self, response):
        btns = response.css('script').xpath('text()').getall()
        for btn in btns:
            if 'download-all' and 'url:' in btn:
                array_url = btn.split()
                for url in array_url:
                    if 'url:' in url and '?' not in url:
                        url = url.replace('"', '').replace(',', '').lstrip('url:')
                        yield scrapy.Request(
                            url,
                            meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'},
                            callback=self.parse_btn
                        )

    @handle_error
    def parse_btn(self, response):
        yield self.build_file_from_response(
            response,
            response.request.meta['kf_filename'],
            data_type="record_package"
        )
