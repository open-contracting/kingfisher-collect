from kingfisher_scrapy.base_spiders import LinksSpider, PeriodicSpider
from kingfisher_scrapy.util import components, join, parameters


class GreeceDiavgis(LinksSpider, PeriodicSpider):
    """
    Domain
      Diavgis
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2026-03-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    API documentation
      https://api.diavgis.gr/ocds
    """

    name = "greece_diavgis"
    custom_settings = {
        # The API allows a maximum of 30 requests per 10 seconds per IP address.
        # https://api.diavgis.gr/ocds
        "CONCURRENT_REQUESTS": 1,
        "DOWNLOAD_DELAY": 0.5,
    }

    # BaseSpider
    date_format = "date"
    default_from_date = "2026-03-01"

    # SimpleSpider
    data_type = "release_package"

    # LinksSpider
    formatter = staticmethod(components(-1))
    next_link_formatter = staticmethod(join(components(-1), parameters("cursor")))

    # PeriodicSpider
    # The API returns one package per day, which is the end of each one-day interval.
    pattern = "https://api.diavgis.gr/ocds/releases/{1:%Y-%m-%d}"
