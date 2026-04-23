import orjson
import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import components, join


class Bulgaria(CompressedFileSpider):
    """
    Domain
      Public Procurement Agency (PPA)
    API documentation
      https://data.egov.bg/api-spetsifikatsiya?section=22&item=82
    """

    name = "bulgaria"

    # SimpleSpider
    data_type = "release_package"

    # Local
    base_url = "https://data.egov.bg"

    async def start(self):
        yield scrapy.Request(
            f"{self.base_url}/api/listDatasets",
            method="POST",
            body=orjson.dumps(
                # 502 is the Public Procurement Agency's organization ID.
                {"criteria": {"org_ids": [502], "formats": ["JSON"], "keywords": "OCDS"}, "records_per_page": 100}
            ),
            callback=self.parse_list,
        )

    def parse_list(self, response):
        """
        The response is expected to be a list of dataset objects, e.g.:
        [{"uri": "27b344eb-da25-4974-ac37-2a4b8435702a", ...}, ...]
        """
        for dataset in response.json()["datasets"]:
            yield scrapy.Request(
                f"{self.base_url}/dataset/{dataset['uri']}/resources/download/json",
                callback=self.parse_item,
            )

    def parse_item(self, response):
        """
        The response contains a download token:
        {"uri": "some-download-token"}
        """
        yield self.build_request(
            f"{self.base_url}/dataset/resources/download/zip/json/{response.json()['uri']}/false",
            formatter=join(components(-2, -1), extension="zip"),
        )
