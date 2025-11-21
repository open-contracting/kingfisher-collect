import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider, IndexSpider
from kingfisher_scrapy.util import components


class BrazilMedicamentosTransparentes(CompressedFileSpider, IndexSpider):
    """
    Domain
      Medicamentos Transparentes by Transparência Brasil
    API documentation
      https://medicamentos-api.transparencia.org.br/docs#/DadosAbertos
    Bulk download documentation
      https://medicamentos.transparencia.org.br/dados-abertos
    """

    name = "brazil_medicamentos_transparentes"

    # SimpleSpider
    data_type = "release_package"

    # IndexSpider
    result_count_pointer = "/response/count"
    limit = 100
    parse_list_callback = "parse_page"
    param_limit = "take"
    param_offset = "skip"

    async def start(self):
        yield scrapy.Request(
            f"https://medicamentos-api.transparencia.org.br/dados-abertos?skip=0&take={self.limit}",
            callback=self.parse_list,
        )

    def parse_page(self, response):
        for item in response.json()["response"]["records"]:
            for file in item["files"]:
                url = file["url"]
                yield scrapy.Request(url, meta={"file_name": components(-1)(url)})
