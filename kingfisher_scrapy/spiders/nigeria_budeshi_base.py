import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class NigeriaBudeshiBase(SimpleSpider):
    def start_requests(self):
        yield scrapy.Request(
            'https://budeshi.ng/api/project_list',
            meta={'file_name': 'project_list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        project_list = response.json()
        for project in project_list:
            yield self.build_request(self.url.format(project['id']), formatter=components(-2))
