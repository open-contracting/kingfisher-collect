from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider
from kingfisher_scrapy.util import handle_error


class ChileCompraRecords(ChileCompraBaseSpider):
    name = 'chile_compra_records'

    @handle_error
    def parse(self, response):
        for item in self.base_parse(response, 'record'):
            yield item
