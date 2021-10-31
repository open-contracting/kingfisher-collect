from kingfisher_scrapy.spiders.europe_dynamic_spider_base import EuropeDynamicSpiderBase


class Ghana(EuropeDynamicSpiderBase):
    """
       Domain
         Ghana Electronic Procurement System (GHANEPS)
       Spider arguments
          from_date
            Download only data from this month onward (YYYY-MM format).
            If ``until_date`` is provided, defaults to '2019-07'.
          until_date
            Download only data until this month (YYYY-MM format).
            If ``from_date`` is provided, defaults to the current month.
    """

    name = 'ghana'

    # BaseSpider
    default_from_date = '2019-07'

    url = 'https://www.ghaneps.gov.gh/ocds/services/recordpackage/getrecordpackagelist'


