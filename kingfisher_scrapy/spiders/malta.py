from kingfisher_scrapy.spiders.european_dynamics_base import EuropeanDynamicsBase


class Malta(EuropeanDynamicsBase):
    """
    Domain
      Electronic Public Procurement System (e-PPS)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format).
        If ``until_date`` is provided, defaults to '2019-10'.
      until_date
        Download only data until this month (YYYY-MM format).
        If ``from_date`` is provided, defaults to the current month.
    API documentation
      https://docs.google.com/document/d/1rV_1VoJT3StzMk2Pf0i2-9uN3lD_VjhFQKyfaGUXZ6I/edit
    """

    name = "malta"

    # BaseSpider
    default_from_date = "2019-10"

    # EuropeanDynamicsBase
    base_url = "http://demowww.etenders.gov.mt"
