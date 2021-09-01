import scrapy

from kingfisher_scrapy.base_spider import IndexSpider


class KenyaMakueni(IndexSpider):
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

    # IndexSpider
    count_pointer = ''
    limit = 1000  # > 1000 causes "must be between 1 and 1000"
    use_page = True
    start_page = 0
    param_page = 'pageNumber'
    base_url = f'https://opencontracting.makueni.go.ke/api/ocds/package/all?pageSize={limit}'

    def start_requests(self):
        url = f'https://opencontracting.makueni.go.ke/api/ocds/release/count?pageSize=1000'
        yield scrapy.Request(url, meta={'file_name': 'count.json'}, callback=self.parse_list)
