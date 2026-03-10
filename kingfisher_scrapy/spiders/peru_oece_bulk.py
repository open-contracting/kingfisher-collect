import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider, IndexSpider
from kingfisher_scrapy.util import components


class PeruOECEBulk(CompressedFileSpider, IndexSpider):
    """
    Domain
      Organismo Especializado para las Contrataciones Públicas Eficientes (OECE)
    API documentation
      https://contratacionesabiertas.oece.gob.pe/api
    Bulk download documentation
      https://contratacionesabiertas.oece.gob.pe/descargas
    """

    name = "peru_oece_bulk"

    # SimpleSpider
    data_type = "record_package"

    # IndexSpider
    formatter = staticmethod(components(-1))
    page_count_pointer = "/pagination/num_pages"
    parse_list_callback = "parse_page"

    # Local
    peru_base_url = "https://contratacionesabiertas.oece.gob.pe/api/v1/files?page={0}&paginateBy=10&format=json"

    async def start(self):
        yield scrapy.Request(self.peru_base_url.format(1), callback=self.parse_list)

    # IndexSpider
    def url_builder(self, value, data, response):
        return self.peru_base_url.format(value)

    def parse_page(self, response):
        for item in response.json()["results"]:
            # Some URLs still use the old domain.
            yield scrapy.Request((item["files"]["json"].replace(".osce.", ".oece.")), meta={"file_name": "all.zip"})
