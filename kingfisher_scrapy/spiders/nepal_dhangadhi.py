import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class NepalDhangadhi(SimpleSpider):
    """
    Domain
      Dhangadhi Infrastructure Management System (IMS)
    Bulk download documentation
      https://ims.susasan.org/dhangadhi/about
    """
    name = 'nepal_dhangadhi'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            'https://admin.ims.susasan.org/api/static-data/dhangadhi',
            meta={'file_name': 'list.json'},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        pattern = 'https://admin.ims.susasan.org/ocds/json/dhangadhi-{}.json'
        data = response.json()
        for item in data['data']['fiscal_years']:
            # A URL might redirect to https://admin.ims.susasan.org/login
            yield self.build_request(pattern.format(item['name']), formatter=components(-1),
                                     meta={'dont_redirect': True})

    def parse(self, response):
        # if we got a redirect response we try it again to download that file
        if response.status == 302:
            yield self.build_request(response.request.url, formatter=components(-1),
                                     dont_filter=True)
        else:
            yield from super().parse(response)
