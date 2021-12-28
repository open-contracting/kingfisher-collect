from kingfisher_scrapy.spiders.europe_dynamic_base import EuropeDynamicBase


class Malta(EuropeDynamicBase):
    """
    Domain
      Malta
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format).
        If ``until_date`` is provided, defaults to '2019-10'.
      until_date
        Download only data until this month (YYYY-MM format).
        If ``from_date`` is provided, defaults to the current month.
    API documentation
      https://docs.google.com/document/d/1VnCEywKkkQ7BcVbT7HlW2s_N_QI8W0KE/edit
    """
    name = 'malta'

    # BaseSpider
    default_from_date = '2019-10'

    base_url = 'http://demowww.etenders.gov.mt'

