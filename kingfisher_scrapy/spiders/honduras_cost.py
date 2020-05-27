import hashlib

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class HondurasCoST(BaseSpider):
    name = 'honduras_cost'
    start_urls = ['http://app.sisocs.org/protected/ocdsShow/']

    def parse(self, response):
        if response.status == 200:
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
        else:
            yield self.build_file_error_from_response(response)

    def parse_btn(self, response):
        if response.status == 200:
            yield self.build_file_from_response(
                response,
                response.request.meta['kf_filename'],
                data_type="record_package"
            )

        else:
            yield self.build_file_error_from_response(response)
