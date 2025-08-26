import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.util import handle_http_error, parameters


class DominicanRepublicAPI(IndexSpider):
    """
    Domain
      Dirección General de Contrataciones Públicas (DGCP)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2015-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    Swagger API documentation
      https://datosabiertos.dgcp.gob.do/api-dgcp/docs/index.html
    """

    name = "dominican_republic_api"

    custom_settings = {
        # To avoid hitting the maximum number of request per second too fast
        "CONCURRENT_REQUESTS": 1,
        # Don't let Scrapy handle error codes.
        "RETRY_HTTP_CODES": [],
    }

    # BaseSpider
    default_from_date = "2015-01-01"
    date_format = "date"
    date_required = True
    max_attempts = 3
    retry_http_codes = [429]

    # SimpleSpider
    data_type = "release_package"

    # IndexSpider
    page_count_pointer = "/pages"
    parse_list_callback = "parse_page"

    # Local
    dominican_republic_base_url = "https://datosabiertos.dgcp.gob.do/api-dgcp/v1/ocds/releases"

    def start_requests(self):
        yield scrapy.Request(
            f"{self.dominican_republic_base_url}/all?start_date={self.from_date.strftime(self.date_format)}"
            f"&end_date={self.until_date.strftime(self.date_format)}",
            callback=self.parse_list,
            meta={"file_name": "page1.json"},
        )

    @handle_http_error
    def parse_page(self, response):
        # If 404, http status is 200 but content is null
        for item in response.json()["payload"].get("content") or []:
            yield self.build_request(
                f"{self.dominican_republic_base_url}?ocid={item['ocid']}",
                formatter=parameters("ocid"),
            )
