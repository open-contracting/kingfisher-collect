from kingfisher_scrapy.spiders.portugal_base import PortugalBase


class PortugalReleases(PortugalBase):
    """
    Swagger API documentation
      http://www.base.gov.pt/swagger/index.html
    Spider arguments
      sample
        Download one list of 100 release packages.
      from_date
        Download only the data with the contract signing start date from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2010-01-01'.
      until_date
        Download only the data with the contract signing end date until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    """
    name = 'portugal_releases'
    data_type = 'release_package_list'
    url = 'http://www.base.gov.pt/api/Release/GetReleases?offset=1'
