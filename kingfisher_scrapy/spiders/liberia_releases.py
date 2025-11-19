import json

import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.util import components, handle_http_error


class LiberiaReleases(IndexSpider):
    """
    Domain
      Public Procurement and Concessions Commission (PPCC)
    Bulk download documentation
      https://eprocurement.ppcc.gov.lr/ocds/report/home.action#/record
    """

    name = "liberia_releases"

    # BaseSpider
    skip_pluck = "Already covered (see code for details)"  # liberia_records

    # SimpleSpider
    data_type = "release_package"

    # IndexSpider
    result_count_pointer = "/total"
    limit = 1000  # unverified
    use_page = True
    start_page = 1
    formatter = None
    parse_list_callback = "parse_items"

    # Local
    url_prefix = "https://eprocurement.ppcc.gov.lr/ocds/record/"

    async def start(self):
        url, kwargs = self.url_builder(self.start_page, None, None)
        yield scrapy.Request(url, **kwargs, callback=self.parse_list)

    def url_builder(self, value, data, response):
        # This endpoint is undocumented.
        return f"{self.url_prefix}searchRecords.action", {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"page": value, "pagesize": self.limit, "sortField": "ocid", "sortDir": "asc"}),
            "meta": {"file_name": f"page-{value}.json"},
        }

    @handle_http_error
    def parse_items(self, response):
        for item in response.json()["items"]:
            # This endpoint is undocumented. There is also a VERSIONED.action endpoint.
            yield self.build_request(
                f"{self.url_prefix}downloadRecord/{item['id']}/COMPILED.action", formatter=components(-2)
            )
