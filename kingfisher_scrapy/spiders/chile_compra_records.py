from kingfisher_scrapy.spiders.chile_base import ChileCompraBaseSpider


class ChileCompraRecords(ChileCompraBaseSpider):
    name = 'chile_compra_records'

    def parse(self, response):
        if response.status == 200:
            for item in self.base_parse(response, 'record'):
                yield item
        else:
            yield {
                'success': False,
                'file_name': response.request.meta['kf_filename'],
                'url': response.request.url,
                'errors': {'http_code': response.status}
            }
