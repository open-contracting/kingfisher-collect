import scrapy

from kingfisher_scrapy import util
from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class BrazilCompras(LinksSpider):
    """
    Domain
      Portal de Compras do Governo Federal
    Caveats
      There is data since 2021-08-10, but the download is slow because of the number of requests per minute limit (100)
      and the number of requests required (at minimum 12 requests per year per buyer, with more than 10k buyers) so the
      spider uses 2024 as the default from date for the download to finish in a reasonable time.
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2024-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    API documentation
      https://dadosabertos.compras.gov.br/swagger-ui/index.html#/11%20-%20OCDS/releases
    """

    custom_settings = {
        # Reduce the number of concurrent requests to avoid multiple failures (undocumented 100 request per minute
        # limit).
        "CONCURRENT_REQUESTS": 1,
        # Don't let Scrapy handle HTTP 429.
        "RETRY_HTTP_CODES": [],
    }

    name = "brazil_compras"

    # BaseSpider
    date_required = True
    default_from_date = "2024-01-01"
    max_attempts = 5
    retry_http_codes = [429]

    # SimpleSpider
    data_type = "release_package"

    # LinksSpider
    formatter = staticmethod(parameters("page", "releaseStartDate", "releaseEndDate", "buyerID"))

    # Local
    base_url = "https://dadosabertos.compras.gov.br/"

    def start_requests(self):
        yield scrapy.Request(
            f"{self.base_url}modulo-uasg/2_consultarOrgao?pagina=1&statusOrgao=true",
            meta={"file_name": "page-1.json"},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        for item in data["resultado"]:
            # The biggest time frame the API allows is 1 month and offset 100
            for start, end in util.date_range_by_interval(self.from_date, self.until_date, 30):
                yield self.build_request(
                    f"{self.base_url}modulo-ocds/1_releases?page=1&offSet=100"
                    f"&buyerID={item['cnpjCpfOrgao']}&"
                    f"releaseStartDate={start:%Y-%m-%d}&"
                    f"releaseEndDate={end:%Y-%m-%d}",
                    formatter=self.formatter,
                )
        remaining_pages = data["paginasRestantes"]
        if remaining_pages > 0:
            next_page = data["totalPaginas"] - remaining_pages + 1
            yield scrapy.Request(
                f"{self.base_url}modulo-uasg/2_consultarOrgao?pagina={next_page}&statusOrgao=true",
                meta={"file_name": f"page-{next_page}.json"},
                callback=self.parse_list,
            )

    @handle_http_error
    def parse(self, response):
        # The API returns a package without releases if no results where found
        if "releases" in response.json():
            yield from super().parse(response)
        else:
            return
