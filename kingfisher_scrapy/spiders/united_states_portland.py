from urllib.parse import urlencode

import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider


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
            # A direct link to the JSON file stored in a Google Drive.
            # The link to the Google Drive folder is published in
            # https://www.portland.gov/business-opportunities/ocds/ocds-data-publication
            "https://drive.google.com/uc?export=download&id=10FoGezSloloNP99iWnqUYXZ3mOPuU-Jt",
            meta={"file_name": "all.html"},
            callback=self.parse_response,
        )

    def parse_response(self, response):
        # The file is big, so we get the HTML confirmation page with the final link to download the file
        form = response.xpath('//form[@id="download-form"]')
        action_url = form.xpath("@action").get()
        params = {}
        for key in ("id", "export", "confirm", "uuid"):
            params[key] = form.xpath(f".//input[@name='{key}']/@value").get()

        yield scrapy.Request(
            url=f"{action_url}?{urlencode(params)}",
            meta={"file_name": "all.json"},
        )
