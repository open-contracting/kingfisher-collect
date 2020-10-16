from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider
from kingfisher_scrapy.util import components


class ChileCompraReleases(ChileCompraBaseSpider):
    """
    Swagger API documentation
      https://desarrolladores.mercadopublico.cl/docs/services/5a9ed02f718ed712f4403e75/operations/data-listaa-omes-agno-mes?
    """
    name = 'chile_compra_releases'
    data_type = 'release_package'

    def handle_item(self, item):
        for key in item:
            if key.startswith('url'):
                yield self.build_request(item[key], formatter=components(-2))
