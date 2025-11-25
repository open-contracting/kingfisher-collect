import scrapy

from kingfisher_scrapy import util
from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class BrazilCompras(LinksSpider):
    """
    Domain
      Portal de Compras do Governo Federal
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2021-08-10'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    API documentation
      https://dadosabertos.compras.gov.br/swagger-ui/index.html#/11%20-%20OCDS/releases
    """

    custom_settings = {
        # Reduce the number of concurrent requests to respect undocumented limit (100/min).
        "CONCURRENT_REQUESTS": 1,
        # Don't let Scrapy handle HTTP 429.
        "RETRY_HTTP_CODES": [],
    }

    name = "brazil_compras"

    # BaseSpider
    date_required = True
    # This is the first date for which there's data for any buyers.
    default_from_date = "2021-08-10"
    max_attempts = 5
    retry_http_codes = [429]

    # SimpleSpider
    data_type = "release_package"

    # LinksSpider
    formatter = staticmethod(parameters("page", "releaseStartDate", "releaseEndDate", "buyerID"))

    async def start(self):
        yield scrapy.Request(
            "https://dadosabertos.compras.gov.br/modulo-uasg/2_consultarOrgao?statusOrgao=true",
            callback=self.parse_buyer_list,
        )

    @handle_http_error
    def parse_buyer_list(self, response):
        for value in range(2, response.json()["totalPaginas"] + 1):
            yield scrapy.Request(
                util.replace_parameters(response.request.url, pagina=value), callback=self.parse_buyer_page
            )

        yield from self.parse_buyer_page(response)

    @handle_http_error
    def parse_buyer_page(self, response):
        for item in response.json()["resultado"]:
            # The API errors if the difference between the month values is greater than 1; for example, January 1 to
            # February 28 succeeds, but January 31 to March 1 fails. To avoid errors, use the shortest month length.
            # "Erro ao efetuar a consulta Período inicial e final maior que 1 mês."
            for start, end in util.date_range_by_interval(self.from_date, self.until_date, 28):
                yield self.build_request(
                    f"https://dadosabertos.compras.gov.br/modulo-ocds/1_releases?page=1&offSet=100"
                    f"&buyerID={item['cnpjCpfOrgao']}&"
                    f"releaseStartDate={start:%Y-%m-%d}&"
                    f"releaseEndDate={end:%Y-%m-%d}",
                    formatter=self.formatter,
                )

    @handle_http_error
    def parse(self, response):
        # The API returns a package without releases if no results are found.
        if "releases" in response.json():
            yield from super().parse(response)
