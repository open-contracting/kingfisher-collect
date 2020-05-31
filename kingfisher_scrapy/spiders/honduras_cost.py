import hashlib

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_error


class HondurasCoST(SimpleSpider):
    name = 'honduras_cost'
    data_type = 'record_package'

    def start_requests(self):
        yield scrapy.Request(
            'http://app.sisocs.org/protected/ocdsShow/',
            meta={'kf_filename': 'list.html'},
            callback=self.parse_list
        )

    @handle_error
    def parse_list(self, response):
        btns = response.css('script').xpath('text()').getall()
        for btn in btns:
            if 'download-all' and 'url:' in btn:
                array_url = btn.split()
                for url in array_url:
                    if 'url:' in url and '?' not in url:
                        url = url.replace('"', '').replace(',', '').lstrip('url:')
                        yield scrapy.Request(
                            url,
                            meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
                        )
