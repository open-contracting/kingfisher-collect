import hashlib
import json

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class Portugal(BaseSpider):
    name = 'portugal'
    download_warnsize = 0
    download_timeout = 9999

    def start_requests(self):
        url = 'https://dados.gov.pt/api/1/datasets/?q=ocds&organization={}&page_size={}'
        id = '5ae97fa2c8d8c915d5faa3bf'
        page_size = 20
        yield scrapy.Request(
            url.format(id, page_size),
            callback=self.parse_list
        )

    def parse_list(self, response):
        if response.status == 200:
            datas = json.loads(response.text)
            for data in datas['data']:
                for resource in data['resources']:
                    description = resource['description']
                    url = resource['url']
                    if description.count("OCDS") or description.count("ocds"):
                        yield scrapy.Request(
                            url,
                            meta={'kf_filename': hashlib.md5(url.encode('utf-8')).hexdigest() + '.json'}
                        )
        else:
            yield {
                'success': False,
                'kf_filename': 'list.json',
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }

    def parse(self, response):
        yield from self.parse_zipfile(response, data_type='record_package_json_lines',
                                      file_format='json_lines', encoding='iso-8859-1')
