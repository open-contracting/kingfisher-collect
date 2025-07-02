from kingfisher_scrapy.base_spiders import PeriodicSpider
from kingfisher_scrapy.util import components

# curl -I https://ppip.gov.np/bulk-download/2019


class Nepal(PeriodicSpider):
    """
    Domain
      Public Procurement Monitoring Office (PPMO)
    Caveats
      This dataset was last updated by the publisher in 2018.
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2012'.
      until_date
        Download only data until this year (YYYY format). Defaults to '2018'.
    Bulk download documentation
      http://ppip.gov.np/downloads
    """

    name = "nepal"

    # BaseSpider
    ocds_version = "1.0"
    date_format = "year"
    default_from_date = "2012"
    default_until_date = "2018"  # HTTP 500 after 2018

    # SimpleSpider
    data_type = "release_package"

    # PeriodicSpider
    pattern = "https://ppip.gov.np/bulk-download/{}"
    formatter = staticmethod(components(-1))  # year
