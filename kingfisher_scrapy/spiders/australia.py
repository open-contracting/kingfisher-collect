from kingfisher_scrapy.base_spiders import LinksSpider, PeriodicSpider
from kingfisher_scrapy.util import components, parameters


class Australia(LinksSpider, PeriodicSpider):
    """
    Domain
      AusTender
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format). Defaults to '2004-01-01T00:00:00'.
      until_date
        Download only data until this time (YYYY-MM-DDThh:mm:ss format). Defaults to now.
    API documentation
      https://github.com/austender/austender-ocds-api
    Swagger API documentation
      https://app.swaggerhub.com/apis/austender/ocds-api/1.1
    """

    name = "australia"

    # BaseSpider
    date_format = "datetime"
    default_from_date = "2004-01-01T00:00:00"

    # SimpleSpider
    data_type = "release_package"

    # LinksSpider
    formatter = staticmethod(components(-2))
    next_link_formatter = staticmethod(parameters("cursor"))

    # PeriodicSpider
    pattern = (
        "https://api.tenders.gov.au/ocds/findByDates/contractPublished/{0:%Y-%m-%dT%H:%M:%S}Z/{1:%Y-%m-%dT%H:%M:%S}Z"
    )
    step = 7
