import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider


class NigeriaPlateauState(SimpleSpider):
    """
    Domain
      Plateau State Open Contracting Portal
    Bulk download documentation
      https://ocds.plateaustate.gov.ng/
    """

    name = "nigeria_plateau_state"

    # SimpleSpider
    data_type = "release_package"

    def start_requests(self):
        yield scrapy.Request(
            "https://api.ocds.plateaustate.gov.ng/api/v1/releases/bulk?download=json", meta={"file_name": "all.json"}
        )
