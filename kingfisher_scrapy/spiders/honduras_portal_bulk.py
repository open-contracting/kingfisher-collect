from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.exceptions import SpiderArgumentError
from kingfisher_scrapy.util import components, handle_http_error


class HondurasPortalBulk(SimpleSpider):
    """
    Domain
      Oficina Normativa de Contratación y Adquisiciones del Estado (ONCAE) / Secretaria de Finanzas de Honduras (SEFIN)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format).
        If ``until_date`` is provided, defaults to '2005-11'.
      until_date
        Download only data until this month (YYYY-MM format).
        If ``from_date`` is provided, defaults to the current month.
      publisher
        Filter by publisher:

        oncae
          Oficina Normativa de Contratación y Adquisiciones del Estado
        sefin
          Secretaria de Finanzas de Honduras
      system
        Filter by oncae system:

        CE
          Catálogo Electrónico
        DDC
          Módulo de Difusión Directa de Contratos
        HC1
          HonduCompras 1.0 (Módulo de Difusión de Compras y Contrataciones)
    Bulk download documentation
      http://www.contratacionesabiertas.gob.hn/descargas/
    """

    name = "honduras_portal_bulk"

    # BaseSpider
    date_format = "year-month"
    default_from_date = "2005-11"
    skip_pluck = "Already covered (see code for details)"  # honduras_portal_api_releases

    # SimpleSpider
    data_type = "release_package"

    # Local
    available_publishers = {
        "oncae": "Oficina Normativa de Contratación y Adquisiciones del Estado (ONCAE) / Honduras",
        "sefin": "Secretaria de Finanzas de Honduras",
    }
    available_systems = {
        "HC1": "HonduCompras 1.0 - Módulo de Difusión de Compras y Contrataciones",
        "CE": "Catálogo Electrónico",
        "DDC": "Módulo de Difusión Directa de Contratos",
    }

    async def start(self):
        url = "http://www.contratacionesabiertas.gob.hn/api/v1/descargas/?format=json"
        yield scrapy.Request(url, callback=self.parse_list)

    @classmethod
    def from_crawler(cls, crawler, publisher=None, system=None, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, publisher=publisher, system=system, **kwargs)
        if publisher and spider.publisher not in spider.available_publishers:
            raise SpiderArgumentError(f"spider argument `publisher`: {spider.publisher!r} not recognized")

        if system:
            if spider.publisher != "oncae":
                raise SpiderArgumentError(
                    f"spider argument `system` is not supported for publisher: {spider.publisher!r}"
                )
            if spider.system not in spider.available_systems:
                raise SpiderArgumentError(f"spider argument `system`: {spider.system!r} not recognized")

        return spider

    @handle_http_error
    def parse_list(self, response):
        """
        The response looks like:

        [
          {
           "urls": {
             "csv": "...",
             "md5": "...",
             "json": "...",
             "xlsx": "..."
           },
           "year": "values between 2005 to the current year",
           "month": "values between 1 and 12",
           "sistema": "values from available_system",
           "publicador": "values from available_publishers"
          }, ...
        ]
        """
        formatter = components(-1)
        for item in response.json():
            publisher = item["publicador"]
            if self.publisher and publisher != self.available_publishers.get(self.publisher):
                continue

            if publisher == self.available_publishers["oncae"]:
                system = item["sistema"]
                if self.system and system != self.available_systems.get(self.system):
                    continue

            if self.from_date and self.until_date:
                date = datetime(int(item["year"]), int(item["month"]), 1)
                if not (self.from_date <= date <= self.until_date):
                    continue

            yield self.build_request(item["urls"]["json"], formatter=formatter)
