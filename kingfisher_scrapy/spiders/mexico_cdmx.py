import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class MexicoCDMXSource(SimpleSpider):
    name = 'mexico_cdmx'
    data_type = 'release_package'
    skip_latest_release_date = 'URL doesnt work anymore'

    def start_requests(self):
        yield scrapy.Request(
            'http://www.contratosabiertos.cdmx.gob.mx/api/contratos/todos',
            meta={'file_name': 'list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        items = json.loads(response.text)
        if self.sample:
            items = [items[0]]

        for item in items:
            # URL looks like http://www.contratosabiertos.cdmx.gob.mx/api/contrato/OCDS-87SD3T-SEDEMA-LP-0027-2017
            yield self.build_request(item['uri'], formatter=components(-1))
