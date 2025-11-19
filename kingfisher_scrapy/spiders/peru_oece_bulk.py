import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider, IndexSpider
from kingfisher_scrapy.util import components, handle_http_error


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

    peru_base_url = "https://contratacionesabiertas.oece.gob.pe/api/v1/files?page={0}&paginateBy=10&format=json"

    async def start(self):
        yield scrapy.Request(self.peru_base_url.format(1), meta={"file_name": "list.json"}, callback=self.parse_list)

    def url_builder(self, value, data, response):
        return self.peru_base_url.format(value)

    @handle_http_error
    def parse_page(self, response):
        for item in response.json()["results"]:
            # Some URLs are still using the old domain (osce)
            yield scrapy.Request((item["files"]["json"].replace(".osce.", ".oece.")), meta={"file_name": "data.zip"})
