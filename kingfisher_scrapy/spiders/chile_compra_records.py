from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider
from kingfisher_scrapy.util import components


class ChileCompraRecords(ChileCompraBaseSpider):
    """
    Swagger API documentation
      https://desarrolladores.mercadopublico.cl/docs/services/5a9ed02f718ed712f4403e75/operations/data-listaa-omes-agno-mes?
    Spider arguments
      sample
        Download only data released on October 2017.
    """
    name = 'chile_compra_records'
    data_type = 'record_package'

    def handle_item(self, item):
        url = 'https://apis.mercadopublico.cl/OCDS/data/record/' + item['ocid'].replace('ocds-70d2nz-', '')
        yield self.build_request(url, formatter=components(-2))
