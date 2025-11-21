import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider


class NigeriaOyoState(SimpleSpider):
    """
    Domain
      Oyo State Open Contracting Portal
    Caveats
      This dataset was last updated by the publisher in 2022.
    """

    name = "nigeria_oyo_state"

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        # From https://ocdsoyo.oyostate.gov.ng/projects.php
        yield scrapy.Request("https://ocdsoyo.oyostate.gov.ng/json_formation.php", meta={"file_name": "all.json"})
