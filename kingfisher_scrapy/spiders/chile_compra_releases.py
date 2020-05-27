from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider
from kingfisher_scrapy.util import handle_error


class ChileCompraReleases(ChileCompraBaseSpider):
    name = 'chile_compra_releases'

    @handle_error()
    def parse(self, response):
        for item in self.base_parse(response, 'release'):
            yield item
