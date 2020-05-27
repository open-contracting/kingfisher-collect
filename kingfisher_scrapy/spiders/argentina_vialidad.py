import scrapy

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import handle_error


class ArgentinaVialidad(BaseSpider):
    name = 'argentina_vialidad'

    def start_requests(self):
        yield scrapy.Request(
            url='https://datosabiertos.vialidad.gob.ar/api/ocds/package/all',
            meta={'kf_filename': 'all.json'}
        )

    @handle_error
    def parse(self, response):
        yield self.build_file_from_response(response, 'all.json', data_type='release_package_list')
