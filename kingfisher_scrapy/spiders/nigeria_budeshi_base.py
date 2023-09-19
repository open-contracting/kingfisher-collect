from abc import abstractmethod
from operator import itemgetter

import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error


class NigeriaBudeshiBase(SimpleSpider):
    # NigeriaBudeshiBase
    base_url = 'https://budeshi.ng/api/'

    def start_requests(self):
        yield scrapy.Request(f'{self.base_url}project_list', meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for project in sorted(response.json(), key=itemgetter('year'), reverse=True):
            yield from self.build_urls(project)

    @abstractmethod
    def build_urls(self, project):
        pass
