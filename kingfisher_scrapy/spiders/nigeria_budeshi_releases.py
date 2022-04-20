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
    skip_pluck = 'Already covered (see code for details)'  # nigeria*_budeshi_records

    # SimpleSpider
    data_type = 'release_package'

    def build_urls(self, project):
        for tag in ('planning', 'tender', 'award', 'contract'):
            yield self.build_request(f'{self.url_prefix}releases/{project["id"]}/{tag}', formatter=components(-2))

    def parse(self, response):
        data = response.json()
        # Some responses include a release list with null objects, e.g.:
        #
        #   "releases": [
        #     null
        #   ]
        if data['releases'] == [None]:
            yield self.build_file_error_from_response(response, errors=data)
        else:
            yield from super().parse(response)
