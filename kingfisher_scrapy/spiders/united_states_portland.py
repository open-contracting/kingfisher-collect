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
        # Get the page with the link to the most recent Google Drive folder containing the JSON file.
        yield scrapy.Request(
            "https://www.portland.gov/business-opportunities/ocds/ocds-data-publication", callback=self.parse_page
        )

    @handle_http_error
    def parse_page(self, response):
        # Follow the link to the most recent Google Drive folder containing the JSON file.
        yield scrapy.Request(response.css('a[href*="drive.google.com"]::attr(href)').get(), callback=self.parse_folder)

    @handle_http_error
    def parse_folder(self, response):
        # The id of the file to download is in the `data-id` attribute of a `tr` element that contains a JSON filename.
        for tr in response.css("tr[data-id]"):
            if "json" in tr.get():
                yield scrapy.Request(
                    f"https://drive.google.com/uc?export=download&id={tr.attrib['data-id']}", callback=self.parse_file
                )

    @handle_http_error
    def parse_file(self, response):
        # Submit form: "FILE is too large for Google to scan for viruses. Would you still like to download this file?"
        form = response.xpath('//form[@id="download-form"]')
        params = {
            key: form.xpath(f".//input[@name='{key}']/@value").get() for key in ("id", "export", "confirm", "uuid")
        }
        yield scrapy.Request(f"{form.xpath('@action').get()}?{urlencode(params)}", meta={"file_name": "all.json"})
