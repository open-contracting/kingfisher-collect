from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider


class ChileCompraRecords(ChileCompraBaseSpider):
    name = 'chile_compra_records'
    data_type = 'record_package'
