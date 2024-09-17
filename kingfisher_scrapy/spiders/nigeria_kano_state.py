from kingfisher_scrapy.spiders.european_dynamics_base import EuropeanDynamicsBase


class NigeriaKanoState(EuropeanDynamicsBase):
    """
    Domain
      Nigeria Kano State Open Contracting Portal
    Spider arguments
       from_date
         Download only data from this month onward (YYYY-MM format).
         If ``until_date`` is provided, defaults to '2021-11'.
       until_date
         Download only data until this month (YYYY-MM format).
         If ``from_date`` is provided, defaults to the current month.
    """

    name = 'nigeria_kano_state'

    # BaseSpider
    default_from_date = '2021-11'

    # EuropeanDynamicsBase
    base_url = 'https://kano-eproc.eurodyn.com'
