from urllib.parse import urlencode

import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import handle_http_error


class UnitedStatesPortland(SimpleSpider):
    """
    Domain
      City of Portland
    Bulk download documentation
      https://www.portland.gov/business-opportunities/ocds/ocds-data-publication
    """

    name = "united_states_portland"

    # SimpleSpider
    data_type = "record_package"

    def start_requests(self):
        yield scrapy.Request(
            # The link to the JSON file in the Google Drive folder that is linked from:
            # https://www.portland.gov/business-opportunities/ocds/ocds-data-publication
            "https://drive.usercontent.google.com/download?id=10FoGezSloloNP99iWnqUYXZ3mOPuU-Jt&export=download",
            meta={"file_name": "all.html"},
            callback=self.parse_response,
        )

    @handle_http_error
    def parse_response(self, response):
        # Submit form: "FILE is too large for Google to scan for viruses. Would you still like to download this file?"
        form = response.xpath('//form[@id="download-form"]')
        params = {
            key: form.xpath(f".//input[@name='{key}']/@value").get() for key in ("id", "export", "confirm", "uuid")
        }
        yield scrapy.Request(
            url=f"{form.xpath('@action').get()}?{urlencode(params)}",
            meta={"file_name": "all.json"},
        )
