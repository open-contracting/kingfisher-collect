import json
from urllib.parse import urlsplit

import scrapy

from kingfisher_scrapy.base_spider import ZipSpider
from kingfisher_scrapy.util import components, handle_http_error


class Malta(ZipSpider):
    name = 'malta'
    data_type = 'record_package'

    def start_requests(self):
        yield scrapy.Request(
            'http://demowww.etenders.gov.mt/ocds/services/recordpackage/getrecordpackagelist',
            meta={'kf_filename': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        urls = json.loads(response.text)['packagesPerMonth']
        if self.sample:
            urls = [urls[0]]

        netloc = urlsplit(response.request.url).netloc
        for url in urls:
            # URL looks like http://malta-demo-server.eurodyn.com/ocds/services/recordpackage/getrecordpackage/2020/1
            yield self.build_request(urlsplit(url)._replace(netloc=netloc).geturl(), formatter=components(-2))
