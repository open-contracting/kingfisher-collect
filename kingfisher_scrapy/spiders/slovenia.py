import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components


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

    async def start(self):
        yield scrapy.Request("http://tbfy.ijs.si/public/ocds/mju/", callback=self.parse_list)

    def parse_list(self, response):
        for number, url in enumerate(reversed(response.xpath("//a/@href").getall())):
            if "ocds" and "json" in url:
                yield self.build_request(response.urljoin(url), formatter=components(-1), priority=number * -1)
