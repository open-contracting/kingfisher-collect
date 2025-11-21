import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class Slovenia(SimpleSpider):
    """
    Domain
      Ministry of Public Administration
    Bulk download documentation
      http://tbfy.ijs.si/?m=tenders&a=list_data&t=si_ocds
    """

    name = "slovenia"

    # SimpleSpider
    data_type = "release_package"

    # Local
    url_prefix = "http://tbfy.ijs.si/public/ocds/mju/"

    async def start(self):
        yield scrapy.Request(self.url_prefix, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for number, url in enumerate(reversed(response.xpath("//a/@href").getall())):
            if "ocds" and "json" in url:
                yield self.build_request(f"{self.url_prefix}{url}", formatter=components(-1), priority=number * -1)
