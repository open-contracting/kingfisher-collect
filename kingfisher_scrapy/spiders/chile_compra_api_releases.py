from kingfisher_scrapy.spiders.chile_compra_api_base import ChileCompraAPIBase
from kingfisher_scrapy.util import components


class ChileCompraAPIReleases(ChileCompraAPIBase):
    """
    Domain
      ChileCompra
    Caveats
      The API is slow and can take months to download all the data it offers.
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2022-01'.
      until_date
        Download only data until this month (YYYY-MM format). Defaults to the current month.
      system
        Filter by system, if not set gets all:
          convenio
            Framework agreements only
          trato-directo
            Direct tenders only
          licitacion
            Traditional tenders
    Swagger API documentation
      https://datos-abiertos.chilecompra.cl/descargas/procesos-ocds
    """

    name = "chile_compra_api_releases"

    # SimpleSpider
    data_type = "release_package"

    def handle_item(self, item):
        for key in item:
            if key.startswith("url"):
                # The API returns URLs with HTTP, which raises timeouts
                yield self.build_request(item[key].replace("http", "https"), formatter=components(-2))
