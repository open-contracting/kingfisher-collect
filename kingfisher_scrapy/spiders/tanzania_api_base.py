import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class TanzaniaAPIBase(LinksSpider):
    # BaseSpider
    skip_pluck = "Already covered (see code for details)"  # tanzania_bulk_releases

    # LinksSpider
    formatter = staticmethod(parameters("cursor", "since"))

    async def start(self):
        yield scrapy.Request(
            f"https://nest.go.tz/gateway/nest-data-portal-api/api/{self.data_type.replace('_package', '')}s",
            meta={"file_name": "offset-0.json"},
        )
