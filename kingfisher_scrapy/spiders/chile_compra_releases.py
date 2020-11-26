from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider
from kingfisher_scrapy.util import components


class ChileCompraReleases(ChileCompraBaseSpider):
    """
    Domain
      ChileCompra
    Spider arguments
      from_date
        Download only releases from this date onward (YYYY-MM format).
        If from_date is not provided defaults to 2008-01
      until_date
        Download only releases until this date (YYYY-MM format).
        If from_date is not provided defaults to current year and month.
      system
        Filter by system, if not set gets all:
          convenio
            Framework agreements only
          trato-directo
            Direct tenders only
          licitacion
            Traditional tenders
    Swagger API documentation
      https://desarrolladores.mercadopublico.cl/docs/services/5a9ed02f718ed712f4403e75/operations/data-listaa-omes-agno-mes
    """
    name = 'chile_compra_releases'
    data_type = 'release_package'

    def handle_item(self, item):
        for key in item:
            if key.startswith('url'):
                yield self.build_request(item[key], formatter=components(-2))
