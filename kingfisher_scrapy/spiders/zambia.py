from kingfisher_scrapy.spiders.european_dynamics_base import EuropeanDynamicsBase


class Zambia(EuropeanDynamicsBase):
    """
    Domain
      Zambia Public Procurement Authority (ZPPA)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format).
        If ``until_date`` is provided, defaults to '2016-07'.
      until_date
        Download only data until this month (YYYY-MM format).
        If ``from_date`` is provided, defaults to the current month.
    """

    name = "zambia"
    default_from_date = "2016-07"

    # BaseSpider
    ocds_version = "1.0"

    # EuropeanDynamicsBase
    base_url = "https://www.zppa.org.zm"
