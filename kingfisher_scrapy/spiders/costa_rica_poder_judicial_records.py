import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class CostaRicaPoderJudicialRecords(SimpleSpider):
    """
    Domain
      Poder Judicial de Costa Rica
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format).
        If ``until_date`` is provided, defaults to '2018'.
      until_date
        Download only data until this year (YYYY format).
        If ``from_date`` is provided, defaults to the current year.
    Bulk download documentation
      https://ckanpj.azurewebsites.net/dataset/estandar-de-datos-de-contrataciones-abiertas-ocds
    """

    name = "costa_rica_poder_judicial_records"

    # BaseSpider
    skip_pluck = "Already covered (see code for details)"  # costa_rica_poder_judicial_releases

    # SimpleSpider
    data_type = "record_package"
    date_format = "year"
    default_from_date = "2018"

    async def start(self):
        yield scrapy.Request(
            "https://ckanpj.azurewebsites.net/api/3/action/package_show?id=estandar-de-datos-de-contrataciones-abiertas-ocds",
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        for resource in response.json()["result"]["resources"]:
            if resource["format"].upper() == "JSON":
                formatter = components(-1)
                if self.from_date and self.until_date:
                    # URL looks like:
                    # https://ckanpj.azurewebsites.net/datosabiertos/OpenContracting/2021.json
                    year = int(formatter(resource["url"]))
                    if not (self.from_date.year <= year <= self.until_date.year):
                        continue
                yield self.build_request(resource["url"], formatter=formatter)
