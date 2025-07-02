from json import JSONDecodeError

from kingfisher_scrapy.base_spiders import LinksSpider, PeriodicSpider
from kingfisher_scrapy.util import components, handle_http_error


class DominicanRepublicAPI(LinksSpider, PeriodicSpider):
    """
    Domain
      Dirección General de Contrataciones Públicas (DGCP)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2018-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    API documentation
      https://api.dgcp.gob.do/api/docs
    """

    name = "dominican_republic_api"
    custom_settings = {
        # Reduce the number of concurrent requests to avoid multiple failures.
        "CONCURRENT_REQUESTS": 1,
    }

    # BaseSpider
    default_from_date = "2018-01-01"
    date_format = "date"

    # SimpleSpider
    data_type = "release_package"

    # LinksSpider
    formatter = staticmethod(components(-2))  # year
    next_pointer = "/pagination/next"

    # Local
    base_url = "https://api.dgcp.gob.do/api/"

    # PeriodicSpider
    pattern = base_url + "date/{0:%Y-%m-%d}/{1:%Y-%m-%d}/1"

    def parse(self, response):
        if response.status == 404:
            try:
                data = response.json()
            except JSONDecodeError:
                pass
            else:
                # API should return an empty package with 200 status.
                if data == {"msg": "No hay resultados."}:
                    return

        yield from handle_http_error(DominicanRepublicAPI.parse_success)(self, response)

    def parse_success(self, response):
        for item in response.json()["data"]:
            yield self.build_request(
                f"{self.base_url}release/{item['ocid']}", formatter=components(-1), callback=super().parse
            )
        yield self.next_link(response)
