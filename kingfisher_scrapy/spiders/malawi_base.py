import orjson
import scrapy

from kingfisher_scrapy.base_spiders import IndexSpider
from kingfisher_scrapy.util import components


class MalawiBase(IndexSpider):
    # IndexSpider
    result_count_pointer = "/total"
    limit = 1000
    formatter = None
    parse_list_callback = "parse_items"

    # Local
    url_prefix = "https://maneps.mw/rms/api/ocds/"

    async def start(self):
        url, kwargs = self.url_builder(0, None, None)
        yield scrapy.Request(url, **kwargs, callback=self.parse_list)

    # IndexSpider
    def url_builder(self, value, data, response):
        return f"{self.url_prefix}get-records", {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": orjson.dumps({"skip": value, "take": self.limit}),
            "meta": {"file_name": f"page-{value}.json"},
        }

    def parse_items(self, response):
        for item in response.json()["items"]:
            # data_type "record_package" corresponds to the record-package endpoint, and "release_package" to the
            # release-package endpoint.
            yield self.build_request(
                f"{self.url_prefix}{self.data_type.replace('_', '-')}/{item['ocid']}", formatter=components(-1)
            )
