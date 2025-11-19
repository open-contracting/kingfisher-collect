import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.util import MAX_DOWNLOAD_TIMEOUT, components, handle_http_error


class ColombiaBulk(CompressedFileSpider):
    """
    Domain
      Colombia Compra Eficiente (CCE)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2011'.
        Only supported for 'SECOP1' system.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
        Only supported for 'SECOP1' system.
      system
        Filter by system:

          SECOP1
            Sistema Electrónico para la Contratación Pública (todos los procesos de contratación)
          SECOP2
            Sistema Electrónico para la Contratación Pública (todos los procesos de contratación)
          TVEC
            Tienda Virtual del Estado Colombiano (acuerdos marco, agregación de demanda, mínima cuantía)
    Bulk download documentation
      https://www.colombiacompra.gov.co/transparencia/datos-json
    """

    name = "colombia_bulk"
    download_timeout = MAX_DOWNLOAD_TIMEOUT
    custom_settings = {
        "DOWNLOAD_FAIL_ON_DATALOSS": False,
    }

    # BaseSpider
    date_format = "year"
    default_from_date = "2011"
    line_delimited = True
    root_path = "Release"
    skip_pluck = "Already covered (see code for details)"  # colombia_api

    # SimpleSpider
    data_type = "release"
    encoding = "iso-8859-1"

    # Local
    available_systems = {"SECOP1": "SI", "SECOP2": "SECOP2", "TVEC": "TVEC"}

    @classmethod
    def from_crawler(cls, crawler, system=None, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, system=system, **kwargs)

        if system and spider.system not in spider.available_systems:
            raise SpiderArgumentError(f"spider argument `system`: {spider.system!r} not recognized")

        if spider.from_date and spider.until_date and spider.system != "SECOP1":
            raise SpiderArgumentError("spider date arguments are only supported for SECOP1 system")

        return spider

    async def start(self):
        yield scrapy.Request(
            "https://www.colombiacompra.gov.co/transparencia/datos-json",
            meta={"file_name": "list.html"},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        for url in response.xpath('//a[@class="enlaces_contenido"]/@href').getall():
            if self.system and self.available_systems[self.system] not in url:
                continue

            if self.from_date and self.until_date:
                # URL looks like https://apiocds.colombiacompra.gov.co/ArchivosSECOP/Archivos/SI2011.zip
                year = int(url[-8:-4])
                if not (self.from_date.year <= year <= self.until_date.year):
                    continue

            yield self.build_request(url, formatter=components(-1))
