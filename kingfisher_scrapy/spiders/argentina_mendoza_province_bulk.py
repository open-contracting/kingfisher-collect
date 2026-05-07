import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components


class ArgentinaMendozaProvinceBulk(SimpleSpider):
    """
    Domain
      Gobierno de la Provincia de Mendoza
    Bulk download documentation
      https://datosabiertos-compras.mendoza.gov.ar/datasets/
    """

    name = "argentina_mendoza_province_bulk"

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        yield scrapy.Request("https://datosabiertos-compras.mendoza.gov.ar/datasets/", callback=self.parse_list)

    def parse_list(self, response):
        for file_url in response.xpath("//div/a/@href").getall():
            if file_url.endswith(".json"):
                yield self.build_request(response.urljoin(file_url), formatter=components(-1))
