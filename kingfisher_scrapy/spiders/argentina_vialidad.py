import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider


class ArgentinaVialidad(SimpleSpider):
    name = 'argentina_vialidad'
    data_type = 'release_package_list'

    def start_requests(self):
        url = 'https://datosabiertos.vialidad.gob.ar/api/ocds/package/all'
        yield scrapy.Request(url, meta={'file_name': 'all.json'})
