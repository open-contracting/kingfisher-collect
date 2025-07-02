from kingfisher_scrapy.spiders.european_dynamics_base import EuropeanDynamicsBase


class LiberiaRecords(EuropeanDynamicsBase):
    """
    Domain
      Public Procurement and Concessions Commission (PPCC)
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format).
        If ``until_date`` is provided, defaults to '2024-11'.
      until_date
        Download only data until this month (YYYY-MM format).
        If ``from_date`` is provided, defaults to the current month.
    Bulk download documentation
      https://eprocurement.ppcc.gov.lr/ocds/report/home.action#/recordPackages
    """

    name = "liberia_records"

    # BaseSpider
    default_from_date = "2024-11"

    # EuropeanDynamicsBase
    base_url = "https://eprocurement.ppcc.gov.lr"
