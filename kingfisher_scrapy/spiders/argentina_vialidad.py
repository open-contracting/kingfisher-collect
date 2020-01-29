import scrapy

from kingfisher_scrapy.base_spider import BaseSpider


class ArgentinaVialidad(BaseSpider):
    name = 'argentina_vialidad'

    def start_requests(self):
        yield scrapy.Request(
            'https://datosabiertos.vialidad.gob.ar/api/ocds/package/all'
        )

    def parse(self, response):
        if response.status == 200:
            yield self.save_response_to_disk(response, 'all.json', data_type='release_package_list')
        else:
            yield {
                'success': False,
                'file_name': 'all.json',
                "url": response.request.url,
                "errors": {"http_code": response.status}
            }
