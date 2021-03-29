from kingfisher_scrapy.spiders.nigeria_budeshi_base import NigeriaBudeshiBase
from kingfisher_scrapy.util import components


class NigeriaBudeshiReleases(NigeriaBudeshiBase):
    """
    Domain
      Budeshi Nigeria
    API documentation
      https://budeshi.ng/Api
    """
    name = 'nigeria_budeshi_releases'

    # BaseSpider
    skip_pluck = 'Already covered (see code for details)'  # nigeria_budeshi_records

    # SimpleSpider
    data_type = 'release_package'

    def build_urls(self, project):
        url = 'https://budeshi.ng/api/releases/{id}/{tag}'
        for tag in ('planning', 'tender', 'award', 'contract'):
            yield self.build_request(url.format(id=project['id'], tag=tag), formatter=components(-2))
