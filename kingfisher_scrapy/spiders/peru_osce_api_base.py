import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class PeruOSCEAPIBase(LinksSpider):
    # LinksSpider
    formatter = staticmethod(parameters('searchAfter'))

    def start_requests(self):
        yield scrapy.Request(
            f'https://contratacionesabiertas.osce.gob.pe/api/v1/{self.endpoint}?format=json&order=desc',
            meta={'file_name': '1.json'}
        )
