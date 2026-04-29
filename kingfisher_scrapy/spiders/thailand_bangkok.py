import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import MAX_DOWNLOAD_TIMEOUT


class ThailandBangkok(SimpleSpider):
    """
    Domain
      Bangkok Metropolitan Administration (BMA)
    Bulk download documentation
      https://opencontract.bangkok.go.th/ocds.html
    """

    name = "thailand_bangkok"
    custom_settings = {
        "DOWNLOAD_TIMEOUT": MAX_DOWNLOAD_TIMEOUT,  # the file is about 215MB
    }

    # SimpleSpider
    data_type = "release_package"

    async def start(self):
        yield scrapy.Request(
            "https://opencontract.bangkok.go.th/assets/data/output/combined/ocds_releases.json",
            meta={"file_name": "ocds_releases.json"},
        )
