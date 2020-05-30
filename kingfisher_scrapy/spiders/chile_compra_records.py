from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider
from kingfisher_scrapy.util import handle_error


class ChileCompraRecords(ChileCompraBaseSpider):
    name = 'chile_compra_records'
    data_type = 'record_package'
