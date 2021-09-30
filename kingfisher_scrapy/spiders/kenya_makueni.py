from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class KenyaMakueni(SimpleSpider):
    """
    Domain
      Makueni County
    Swagger API documentation
      https://opencontracting.makueni.go.ke/swagger-ui/#/ocds-controller
    """
    name = 'kenya_makueni'

    # BaseSpider
    root_path = 'item'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield from self.request_page(0)

    @handle_http_error
    def parse(self, response):
        yield from super().parse(response)

        if response.json():
            page = response.request.meta['page']
            yield from self.request_page(page + 1)

    def request_page(self, page):
        url = f'https://opencontracting.makueni.go.ke/api/ocds/package/all?pageSize=1000&pageNumber={page}'
        yield self.build_request(url, parameters('pageNumber'), meta={'page': page})
