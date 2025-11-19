import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


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

    base_url = "https://datosabiertos-compras.mendoza.gov.ar"

    async def start(self):
        yield scrapy.Request(f"{self.base_url}/datasets/", meta={"file_name": "list.html"}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for file_url in response.xpath("//div/a/@href").getall():
            if file_url.endswith(".json"):
                yield self.build_request(f"{self.base_url}{file_url}", formatter=components(-1))
