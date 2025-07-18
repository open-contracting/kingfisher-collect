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
            # A direct link to the JSON file stored in a Google Drive, bypassing the virus scan warning.
            # The link to the Google Drive folder is published in
            # https://www.portland.gov/business-opportunities/ocds/ocds-data-publication
            "https://www.googleapis.com/drive/v3/files/10FoGezSloloNP99iWnqUYXZ3mOPuU-Jt?alt=media"
            "&key=AIzaSyDVCNpmfKmJ0gPeyZ8YWMca9ZOKz0CWdgs",
            meta={"file_name": "all.json"},
        )
