from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider


class ChileCompraReleases(ChileCompraBaseSpider):
    name = 'chile_compra_releases'
    data_type = 'release_package'
