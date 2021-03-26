from operator import itemgetter
from kingfisher_scrapy.spiders.nigeria_budeshi_base import NigeriaBudeshiBase
from kingfisher_scrapy.util import handle_http_error, components


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

    url = 'https://budeshi.ng/api/releases/{id}/{tag}'

    @handle_http_error
    def parse_list(self, response):
        project_list = response.json()
        for project in sorted(project_list, key=itemgetter('year'), reverse=True):
            for tag in ('planning', 'tender', 'award', 'contract'):
                yield self.build_request(self.url.format(id=project['id'], tag=tag), formatter=components(-2))
