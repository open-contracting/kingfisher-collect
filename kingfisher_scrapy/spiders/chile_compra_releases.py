from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider


class ChileCompraReleases(ChileCompraBaseSpider):
    name = 'chile_compra_releases'

    def parse(self, response):
        if response.status == 200:
            for item in self.base_parse(response, 'release'):
                yield item
        else:
            yield self.build_file_error_from_response(response)
