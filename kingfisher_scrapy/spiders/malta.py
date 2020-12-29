import json
from urllib.parse import urlsplit

import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider
from kingfisher_scrapy.util import components, handle_http_error


class Malta(CompressedFileSpider):
    """
    Domain
      Malta
    API documentation
      https://docs.google.com/document/d/1VnCEywKkkQ7BcVbT7HlW2s_N_QI8W0KE/edit
    """
    name = 'malta'
    data_type = 'record_package'

    def start_requests(self):
        yield scrapy.Request(
            'http://demowww.etenders.gov.mt/ocds/services/recordpackage/getrecordpackagelist',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        urls = response.json()['packagesPerMonth']

        netloc = urlsplit(response.request.url).netloc
        for url in urls:
            # URL looks like http://malta-demo-server.eurodyn.com/ocds/services/recordpackage/getrecordpackage/2020/1
            yield self.build_request(urlsplit(url)._replace(netloc=netloc).geturl(), formatter=components(-2))
