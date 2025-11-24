import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class NepalDhangadhi(SimpleSpider):
    """
    Domain
      Infrastructure Management System (IMS)
    Caveats
      Some downloads require a login.
    Bulk download documentation
      https://ims.susasan.org/dhangadhi/about
    """

    name = "nepal_dhangadhi"

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        yield scrapy.Request("https://admin.ims.susasan.org/api/static-data/dhangadhi", callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for number, item in enumerate(reversed(response.json()["data"]["fiscal_years"])):
            # A URL might redirect to https://admin.ims.susasan.org/login
            yield self.build_request(
                f"https://admin.ims.susasan.org/ocds/json/dhangadhi-{item['name']}.json",
                formatter=components(-1),
                meta={"dont_redirect": True},
                priority=number * -1,
            )

    def is_http_error_expected(self, response):
        return response.request.url in {
            "https://admin.ims.susasan.org/ocds/json/dhangadhi-2080-81.json",
            "https://admin.ims.susasan.org/ocds/json/dhangadhi-2081-82.json",
        }
