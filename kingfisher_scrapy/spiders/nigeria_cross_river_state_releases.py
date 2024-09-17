from kingfisher_scrapy.spiders.nigeria_cross_river_state_base import NigeriaCrossRiverStateBase


class NigeriaCrossRiverStateReleases(NigeriaCrossRiverStateBase):
    """
    Domain
      Cross River State
    Spider arguments
      from_date
        Download only data from this month onward (YYYY-MM format).
        If ``until_date`` is provided, defaults to '2019-08'.
      until_date
        Download only data until this month (YYYY-MM format).
        If ``from_date`` is provided, defaults to the current month.
    API documentation
      http://ocdsapi.dppib-crsgov.org/Help
    """

    name = 'nigeria_cross_river_state_releases'

    # SimpleSpider
    data_type = 'release_package'

    def build_url(self, date):
        return f'{self.url_prefix}getReleasePackage?year={date:%Y}&month={date:%m}'
