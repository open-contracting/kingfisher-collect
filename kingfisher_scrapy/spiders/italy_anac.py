import scrapy

from kingfisher_scrapy.base_spiders import BigFileSpider
from kingfisher_scrapy.util import BROWSER_USER_AGENT, MAX_DOWNLOAD_TIMEOUT, components, handle_http_error


class ItalyANAC(BigFileSpider):
    """
    Domain
      Autorità Nazionale Anticorruzione (ANAC)
    Caveats
      If the OCID is missing, the spider derives the ``ocid`` field from the ``id`` field.
    API documentation
      https://dati.anticorruzione.it/opendata/about
    Bulk download documentation
      https://dati.anticorruzione.it/opendata/organization/anticorruzione
    """

    name = "italy_anac"
    download_timeout = MAX_DOWNLOAD_TIMEOUT * 2  # 1h
    user_agent = BROWSER_USER_AGENT  # Otherwise, API returns "Request Rejected" HTML

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        yield scrapy.Request(
            "https://dati.anticorruzione.it/opendata/api/3/action/package_search?q=ocds",
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        for result in response.json()["result"]["results"]:
            for resource in result["resources"]:
                if resource["format"].upper() == "JSON":
                    yield self.build_request(resource["url"], formatter=components(-2))

    # ResizePackageMiddleware
    def ocid_fallback(self, release):
        # Extract the ocid from the release id as a fallback, like ocds-hu01ve-7608611 from ocds-hu01ve-7608611-01.
        return "-".join(release["id"].split("-")[:3])
