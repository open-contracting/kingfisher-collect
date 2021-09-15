from abc import abstractmethod
from operator import itemgetter

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error


class NigeriaKadunaStateBase(SimpleSpider):
    # SimpleSpider
    base_url = 'https://www.budeshi.ng/kadppa/api/'

    def start_requests(self):
        yield scrapy.Request(
            f'{self.base_url}project_list',
            meta={'file_name': 'project_list.json'},
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        project_list = response.json()
        for project in sorted(project_list, key=itemgetter('year'), reverse=True):
            yield from self.build_urls(project['id'])

    @abstractmethod
    def build_urls(self, project):
        pass
