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

    async def start(self):
        yield scrapy.Request(
            # Get the page where the link to the most recent Google Drive folder where the JSON is
            "https://www.portland.gov/business-opportunities/ocds/ocds-data-publication",
            meta={"file_name": "all.html"},
            callback=self.parse_list,
        )

    @handle_http_error
    def parse_list(self, response):
        yield scrapy.Request(
            # Find the link to the Google Drive folder
            response.css('a[href*="drive.google.com"]::attr(href)').get(),
            meta={"file_name": "all.html"},
            callback=self.parse_response,
        )

    @handle_http_error
    def parse_response(self, response):
        # The id of the file to download is in the data-id element of a tr block that contains the name of the file
        # as part of a javascript code
        for file_tr in response.css("tr[data-id]"):
            if "json" in file_tr.get():
                yield scrapy.Request(
                    f"https://drive.google.com/uc?export=download&id={file_tr.attrib['data-id']}",
                    meta={"file_name": "download.html"},
                    callback=self.parse_file,
                )

    @handle_http_error
    def parse_file(self, response):
        # Submit form: "FILE is too large for Google to scan for viruses. Would you still like to download this file?"
        form = response.xpath('//form[@id="download-form"]')
        params = {
            key: form.xpath(f".//input[@name='{key}']/@value").get() for key in ("id", "export", "confirm", "uuid")
        }
        yield scrapy.Request(
            url=f"{form.xpath('@action').get()}?{urlencode(params)}",
            meta={"file_name": "all.json"},
        )
