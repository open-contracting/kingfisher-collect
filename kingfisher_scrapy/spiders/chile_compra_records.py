from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider
from kingfisher_scrapy.util import components


class ChileCompraRecords(ChileCompraBaseSpider):
    name = 'chile_compra_records'
    data_type = 'record_package'
    skip_latest_release_date = 'Already covered by chile_compra_releases'

    def handle_item(self, item):
        url = 'https://apis.mercadopublico.cl/OCDS/data/record/' + item['ocid'].replace('ocds-70d2nz-', '')
        yield self.build_request(url, formatter=components(-2))
