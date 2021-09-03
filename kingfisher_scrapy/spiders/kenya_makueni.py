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

    step = 100
    url = 'https://opencontracting.makueni.go.ke/api/ocds/package/all?pageSize={0}&pageNumber={1}'

    def start_requests(self):
        yield self.build_request(self.url.format(self.step, 0),
                                 self.get_formatter(), meta={'page': 0}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        page = response.request.meta['page']
        yield self.build_file_from_response(response, data_type=self.data_type)

        if len(response.json()) > 0:
            yield self.build_request(self.url.format(self.step, page + 1),
                                     self.get_formatter(), meta={'page': page + 1}, callback=self.parse_list)

    def get_formatter(self):
        return parameters('pageNumber')
