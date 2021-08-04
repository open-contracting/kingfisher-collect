from kingfisher_scrapy.spiders.nigeria_cross_river_base import NigeriaCrossRiverBase


class NigeriaCrossRiverReleases(NigeriaCrossRiverBase):
    """
    Domain
      Cross River Nigeria
    API documentation
      http://ocdsapi.dppib-crsgov.org/Help
    """
    name = 'nigeria_cross_river_state_releases'

    # SimpleSpider
    data_type = 'release_package'

    def build_urls(self, date):
        pattern = self.base_url + 'getReleasePackage?year={0.year:d}&month={0.month:02d}'
        yield pattern.format(date)
