import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components


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

    def parse_list(self, response):
        for number, item in enumerate(reversed(response.json()["data"]["fiscal_years"])):
            # Fiscal years 2080 and later redirect to https://admin.ims.susasan.org/login.
            quiet = int(item["name"][:4]) >= 2080
            yield self.build_request(
                f"https://admin.ims.susasan.org/ocds/json/dhangadhi-{item['name']}.json",
                formatter=components(-1),
                meta={"dont_redirect": True, "quiet": quiet},
                priority=number * -1,
            )

    def parse(self, response):
        # `dont_redirect` is set, so redirects reach the callback.
        if self.is_http_success(response):
            yield from super().parse(response)
        else:
            self.log_error_from_response(response, level="warning" if response.request.meta["quiet"] else "error")
