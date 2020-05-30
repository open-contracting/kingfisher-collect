import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_error


class ArgentinaVialidad(SimpleSpider):
    name = 'argentina_vialidad'
    data_type = 'release_package_list'

    def start_requests(self):
        yield scrapy.Request(
            'https://datosabiertos.vialidad.gob.ar/api/ocds/package/all',
            meta={'kf_filename': 'all.json'}
        )
