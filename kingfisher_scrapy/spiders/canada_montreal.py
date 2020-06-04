import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters, replace_parameter


class CanadaMontreal(SimpleSpider):
    name = 'canada_montreal'
    data_type = 'release_package'
    step = 10000

    def start_requests(self):
        url = 'https://ville.montreal.qc.ca/vuesurlescontrats/api/releases.json?limit={step}'.format(step=self.step)
        yield scrapy.Request(url, meta={'file_name': 'offset-0.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        yield from self.parse(response)

        if not self.sample:
            data = json.loads(response.text)
            offset = data['meta']['pagination']['limit']
            total = data['meta']['count']
            for offset in range(offset, total, self.step):
                url = replace_parameter(response.request.url, 'offset', offset)
                yield self.build_request(url, formatter=parameters('offset'))
