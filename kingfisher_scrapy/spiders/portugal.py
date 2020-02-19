import hashlib
import json
from io import BytesIO
from zipfile import ZipFile

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
        if response.status == 200:
            zip_file = ZipFile(BytesIO(response.body))
            for finfo in zip_file.infolist():
                data = zip_file.open(finfo.filename).read()
                yield self.save_data_to_disk(
                    data,
                    response.request.meta['kf_filename'],
                    data_type='record_package_json_lines',
                    url=response.request.url
                )
        else:
            yield {
                'success': False,
                'kf_filename': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
