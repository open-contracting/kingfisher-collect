import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error


class MexicoAguascalientesPlataformaDigitalEstatal(SimpleSpider):
    """
    Domain
      Mexico Aguascalientes Plataforma Digital Estatal
    Bulk download documentation
      https://plataformadigitalestatal.org/Publica/contratacionesPublicas/index.html
    """

    name = "mexico_aguascalientes_plataforma_digital_estatal"

    # BaseSpider
    root_path = "item"

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        yield scrapy.Request(
            "https://plataformadigitalestatal.org/Publica/contratacionesPublicas/index.html",
            meta={"file_name": "list.html"},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        for url in response.xpath("//a/@href").getall():
            # The URL is currently a link to a Google Drive file.
            # The other existing href are partials within the website, e.g. "#contrataciones".
            if "http" in url:
                yield scrapy.Request(url, meta={"file_name": "all.json"})
