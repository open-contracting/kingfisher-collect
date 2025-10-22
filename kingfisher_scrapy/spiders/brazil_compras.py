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
        # Reduce the number of concurrent requests to avoid multiple failures (undocumented 100 request per minute
        # limit).
        "CONCURRENT_REQUESTS": 1,
        # Don't let Scrapy handle HTTP 429.
        "RETRY_HTTP_CODES": [],
    }

    name = "brazil_compras"

    # BaseSpider
    date_required = True
    # This is the first date they have data for any buyers.
    default_from_date = "2021-08-10"
    max_attempts = 5
    retry_http_codes = [429]

    # SimpleSpider
    data_type = "release_package"

    # LinksSpider
    formatter = staticmethod(parameters("page", "releaseStartDate", "releaseEndDate", "buyerID"))

    # Local
    base_url = "https://dadosabertos.compras.gov.br"
    base_buyers_url = f"{base_url}/modulo-uasg/2_consultarOrgao?statusOrgao=true"

    def start_requests(self):
        yield scrapy.Request(
            f"{self.base_buyers_url}&pagina=1",
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
                    f"{self.base_url}/modulo-ocds/1_releases?page=1&offSet=100"
                    f"&buyerID={item['cnpjCpfOrgao']}&"
                    f"releaseStartDate={start:%Y-%m-%d}&"
                    f"releaseEndDate={end:%Y-%m-%d}",
                    formatter=self.formatter,
                )
        remaining_pages = data["paginasRestantes"]
        if remaining_pages > 0:
            next_page = data["totalPaginas"] - remaining_pages + 1
            yield scrapy.Request(
                f"{self.base_buyers_url}&pagina={next_page}",
                meta={"file_name": f"page-{next_page}.json"},
                callback=self.parse_list,
            )

    @handle_http_error
    def parse(self, response):
        # The API returns a package without releases if no results where found
        if "releases" in response.json():
            yield from super().parse(response)
