import json
from urllib.parse import urlparse

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class HondurasPortalBulkFiles(BaseSpider):
    name = 'honduras_portal_bulk_files'

    def start_requests(self):
        yield scrapy.Request(
            'http://www.contratacionesabiertas.gob.hn/api/v1/descargas/?format=json',
            callback=self.parse_json_list
        )

    def parse_json_list(self, response):
        filelist = json.loads(response.text)

        if self.sample:
            yield scrapy.Request(filelist[0]['urls']['json'])

        else:
            for item in filelist:
                yield scrapy.Request(item['urls']['json'])

    def parse(self, response):

        filename = urlparse(response.request.url).path.split('/')[-2]
        if response.status == 200:
            yield self.save_response_to_disk(
                response,
                filename,
                data_type='release_package'
            )
        else:
            yield {
                'success': False,
                'file_name': filename,
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
