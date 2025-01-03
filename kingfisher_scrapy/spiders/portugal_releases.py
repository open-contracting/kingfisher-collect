from kingfisher_scrapy.spiders.portugal_base import PortugalBase


class PortugalReleases(PortugalBase):
    """
    Domain
      Instituto dos Mercados Públicos, do Imobiliário e da Construção (IMPIC)
    Caveats
      This dataset was last updated by the publisher in 2020.
    Spider arguments
      from_date
        Download only data with a contract signing date from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2010-01-01'.
      until_date
        Download only data with a contract signing date until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    Swagger API documentation
      http://www.base.gov.pt/swagger/index.html
    """

    name = 'portugal_releases'

    # SimpleSpider
    data_type = 'release_package'

    # PortugalBase
    start_url = 'http://www.base.gov.pt/api/Release/GetReleases'
