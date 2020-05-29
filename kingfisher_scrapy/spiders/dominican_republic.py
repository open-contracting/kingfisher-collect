import os
import tempfile

import rarfile
import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class DominicanRepublic(BaseSpider):
    name = 'dominican_republic'
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 360
    }

    def start_requests(self):
        yield scrapy.Request(
            'https://www.dgcp.gob.do/estandar-mundial-ocds/',
            meta={'kf_filename': 'list.html'},
            callback=self.parse_list,
        )

    @handle_error
    def parse_list(self, response):
        urls = response.css('.fileLink::attr(href)').getall()
        json_urls = list(filter(lambda x: '/JSON_DGCP_' in x, urls))

        if self.sample and len(json_urls) > 0:
            json_urls = [json_urls[0]]

        for url in json_urls:
            if '/JSON_DGCP_' in url:
                yield scrapy.Request('https:' + url)

    def parse(self, response):
        if self.is_http_success(response):
            file = tempfile.NamedTemporaryFile(delete=False)
            file.write(response.body)
            file.close()
            with rarfile.RarFile(file.name, charset='utf-8') as tmpfile:
                for f in tmpfile.infolist():
                    with tmpfile.open(f) as jsonFile:
                        yield self.build_file(jsonFile.read(), f.filename, data_type='release_package',
                                              url=response.request.url)
            os.remove(file.name)
        else:
            filename = response.request.url.split('/')[-1]
            yield self.build_file_error_from_response(response, file_name=filename)
