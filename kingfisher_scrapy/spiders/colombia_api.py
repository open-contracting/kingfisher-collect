import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import handle_http_error, parameters, replace_path_separator


class ColombiaAPI(LinksSpider):
    """
    Domain
      Colombia Compra Eficiente (CCE)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2011-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    API documentation
      https://www.colombiacompra.gov.co/transparencia/api
    Swagger API documentation
      https://apiocds.colombiacompra.gov.co/apiCCE-2.0/
    """

    name = "colombia_api"

    # BaseSpider
    default_from_date = "2011-01-01"
    date_required = True

    # SimpleSpider
    data_type = "release_package"

    # LinksSpider
    formatter = staticmethod(parameters("_id", parser=replace_path_separator))  # e.g. _id=11/23

    def start_requests(self):
        from_date = self.from_date.strftime(self.date_format)
        until_date = self.until_date.strftime(self.date_format)
        url = f"https://apiocds.colombiacompra.gov.co/apiCCE-2.0/rest/releases/dates/{from_date}/{until_date}"

        yield scrapy.Request(url, meta={"file_name": f"{from_date}.json"})

    @handle_http_error
    def parse(self, response):
        # Replace unescaped tab characters within strings with a space.
        response = response.replace(body=response.body.replace(b"\t", b" "))
        yield from super().parse(response)
