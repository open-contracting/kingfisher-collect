from datetime import date

import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class Australia(LinksSpider):
    """
    Domain
      AusTender
    API documentation
      https://github.com/austender/austender-ocds-api
    Swagger API documentation
      https://app.swaggerhub.com/apis/austender/ocds-api/1.1
    """

    name = "australia"

    default_from_date = "2004-01-01"

    # SimpleSpider
    data_type = "release_package"

    # LinksSpider
    next_page_formatter = staticmethod(parameters("cursor"))

    def start_requests(self):
        from_date = (
            self.from_date.strftime("%Y-%m-%d")
            if self.from_date is not None
            else self.default_from_date
        )

        until_date = (
            self.until_date.strftime("%Y-%m-%d")
            if self.until_date is not None
            else f"{date.today().year}-12-31"
        )

        url = (
            f"https://api.tenders.gov.au/ocds/findByDates/contractPublished/"
            f"{from_date}T00:00:00Z/{until_date}T23:59:59Z"
        )
        yield scrapy.Request(url, meta={"file_name": "start.json"})
