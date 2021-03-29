from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider
from kingfisher_scrapy.util import components


class ChileCompraRecords(ChileCompraBaseSpider):
    """
    Domain
      ChileCompra
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format). Defaults to '2009-01'.
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
      https://desarrolladores.mercadopublico.cl/docs/services/5a9ed02f718ed712f4403e75/operations/data-listaa-omes-agno-mes
    """
    name = 'chile_compra_records'

    # BaseSpider
    skip_pluck = 'Already covered (see code for details)'  # chile_compra_releases

    # SimpleSpider
    data_type = 'record_package'

    def handle_item(self, item):
        url = 'https://apis.mercadopublico.cl/OCDS/data/record/' + item['ocid'].replace('ocds-70d2nz-', '')
        # URL looks like http://api.mercadopublico.cl/APISOCDS/OCDS/listaOCDSAgnoMesTratoDirecto/2021/03/31500/100
        yield self.build_request(url, formatter=components(-2))
