from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import components


class CanadaBuyandsell(CompressedFileSpider):
    """
    Domain
      Public Works and Government Services Canada
    Caveats
      The dataset is a pilot that ended in 2017.
    API documentation
      https://open.canada.ca/data/en/dataset/60f22648-c173-446f-aa8a-4929d75d63e3
    """

    name = "canada_buyandsell"

    # BaseSpider
    ocds_version = "1.0"

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        yield self.build_request(
            "https://donnees-data.tpsgc-pwgsc.gc.ca/ba2/pilot-oc-pilote-co/releases.zip", formatter=components(-1)
        )
