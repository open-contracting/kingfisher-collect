from datetime import datetime

import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import BROWSER_USER_AGENT, components, handle_http_error


class MexicoNuevoLeon(SimpleSpider):
    """
    Domain
      Nuevo León - Dirección General de Adquisiciones y Servicios - Secretaría de Administración
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2024-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    Bulk download documentation
      https://catalogodatos.nl.gob.mx/dataset/contrataciones-abiertas-direccion-general-de-adquisiciones-y-servicios
    """

    name = "mexico_nuevo_leon"
    user_agent = BROWSER_USER_AGENT  # to avoid HTTP 403

    # BaseSpider
    default_from_date = "2024-01-01"

    # SimpleSpider
    data_type = "release_package"

    def start_requests(self):
        # A CKAN API JSON response.
        url = (
            "https://catalogodatos.nl.gob.mx/api/3/action/package_show?id="
            "contrataciones-abiertas-direccion-general-de-adquisiciones-y-servicios"
        )
        yield scrapy.Request(url, meta={"file_name": "package_show.json"}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        for resource in response.json()["result"]["resources"]:
            # Some files don't include an extension file, so we need to check the file name instead.
            if resource["name"].upper().startswith("JSON-OCDS"):
                if self.from_date and self.until_date:
                    date = datetime.strptime(resource["created"], "%Y-%m-%dT%H:%M:%S.%f").replace(
                        tzinfo=self.from_date.tzinfo
                    )
                    if not (self.from_date <= date <= self.until_date):
                        continue
                yield self.build_request(resource["url"], formatter=components(-1))
