import json
from urllib.parse import urlparse

import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class HondurasPortalBulkFiles(BaseSpider):
    name = 'honduras_portal_bulk_files'

    def start_requests(self):
        yield scrapy.Request(
            'http://www.contratacionesabiertas.gob.hn/api/v1/descargas/?format=json',
            callback=self.parse_json_list
        )

    @handle_error()
    def parse_json_list(self, response):
        filelist = json.loads(response.text)

        if self.sample:
            yield scrapy.Request(filelist[0]['urls']['json'])

        else:
            for item in filelist:
                yield scrapy.Request(item['urls']['json'])

    def parse(self, response):
        filename = urlparse(response.request.url).path.split('/')[-2]
        if self.is_http_success(response):
            yield self.build_file_from_response(
                response,
                filename,
                data_type='release_package'
            )
        else:
            yield self.build_file_error_from_response(response, file_name=filename)
