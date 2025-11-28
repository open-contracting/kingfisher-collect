from kingfisher_scrapy.base_spiders import IndexSpider, PeriodicSpider
from kingfisher_scrapy.util import components, handle_http_error, parameters, replace_path_separator


class EcuadorSERCOPAPI(IndexSpider, PeriodicSpider):
    """
    Domain
      Servicio Nacional de Contratación Pública (SERCOP)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2015'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    API documentation
      https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos/api
    Bulk download documentation
      https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/datos-abiertos
    """

    name = "ecuador_sercop_api"
    custom_settings = {
        # Reduce the number of concurrent requests to avoid multiple failures.
        "CONCURRENT_REQUESTS": 2,
        # Don't let Scrapy handle HTTP 429.
        "RETRY_HTTP_CODES": [],
    }

    # BaseSpider
    date_format = "year"
    default_from_date = "2015"
    max_attempts = 5
    retry_http_codes = [429]

    # SimpleSpider
    data_type = "release_package"

    # Local
    url_prefix = "https://datosabiertos.compraspublicas.gob.ec/PLATAFORMA/api/"

    # PeriodicSpider
    pattern = f"{url_prefix}search_ocds?year={{0}}"
    formatter = staticmethod(components(-1))
    start_callback = "parse_list"

    # IndexSpider
    page_count_pointer = "/pages"
    parse_list_callback = "parse_page"

    @handle_http_error
    def parse_page(self, response):
        for data in response.json()["data"]:
            # Some ocids have a '/' character which cannot be in a file name.
            yield self.build_request(
                f"{self.url_prefix}record?ocid={data['ocid']}",
                formatter=parameters("ocid", parser=replace_path_separator),
            )
