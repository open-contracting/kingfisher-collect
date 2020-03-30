import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class MexicoCDMXSource(BaseSpider):
    name = 'mexico_cdmx'

    def start_requests(self):
        yield scrapy.Request(
            url='http://www.contratosabiertos.cdmx.gob.mx/api/contratos/todos',
            meta={'kf_filename': 'list.json'},
            callback=self.parse_list
        )

    def parse_list(self, response):
        if response.status == 200:

            data = json.loads(response.text)
            if self.sample:
                data = [data[0]]

            for data_item in data:
                yield scrapy.Request(
                    url=data_item['uri'],
                    meta={'kf_filename': 'id%s.json' % data_item['id']},
                    callback=self.parse_record
                )
        else:
            yield {
                'success': False,
                'file_name': 'list.json',
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }

    def parse_record(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(response, response.request.meta['kf_filename'],
                                             data_type='release_package')
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
