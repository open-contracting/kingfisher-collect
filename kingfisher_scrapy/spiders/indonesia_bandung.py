import datetime
import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class IndonesiaBandung(BaseSpider):
    name = 'indonesia_bandung'

    def start_requests(self):
        url = 'https://birms.bandung.go.id/api/packages/year/{}'
        current_year = datetime.datetime.now().year + 1
        for year in range(2013, current_year):
            yield scrapy.Request(
                url.format(year),
                meta={'kf_filename': 'start_requests'},
                callback=self.parse_data
            )

    def parse_data(self, response):
        if response.status == 200:
            json_data = json.loads(response.text).get('data')
            for data in json_data:
                url = data.get('uri')
                if url:
                    yield scrapy.Request(
                        url,
                        meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'},
                    )
                    if self.sample:
                        break
            else:
                next_page_url = json_data.get('next_page')
                if next_page_url:
                    yield scrapy.Request(
                        next_page_url,
                        callback=self.parse_data
                    )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }

    def parse(self, response):
        if response.status == 200:
            json_data = json.loads(response.text)
            if len(json_data) == 0:
                return
            yield self.save_response_to_disk(
                response,
                response.request.meta['kf_filename'],
                data_type='release'
            )
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
