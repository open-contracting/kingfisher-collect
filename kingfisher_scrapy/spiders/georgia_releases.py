import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters

# https://odapi.spa.ge/Json.zip#/tenders?sort=tenderAnnouncementDateSortDesc


class GeorgiaReleases(LinksSpider):
    """
    Domain
      State Procurement Agency (SPA)
    Caveats
      This dataset was last updated by the publisher in 2020.
    Bulk download documentation
      https://odapi.spa.ge/publication-policy
    Swagger API documentation
      https://odapi.spa.ge/api/swagger.ui
    """

    name = "georgia_releases"

    # SimpleSpider
    data_type = "release_package"

    # LinksSpider
    formatter = staticmethod(parameters("page"))

    def start_requests(self):
        url = "https://odapi.spa.ge/api/releases.json"
        yield scrapy.Request(url, meta={"file_name": "page-1.json"})
