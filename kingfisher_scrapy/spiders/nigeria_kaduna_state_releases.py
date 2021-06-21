from kingfisher_scrapy.spiders.nigeria_kaduna_state_base import NigeriaKadunaStateBudeshiBase
from kingfisher_scrapy.util import components


class NigeriaKadunaStateBudeshiReleases(NigeriaKadunaStateBudeshiBase):
    """
    Domain
        Kaduna State
    Bulk download documentation
        https://www.budeshi.ng/kadppa/api
    """
    name = 'nigeria_kaduna_state_releases'

    # SimpleSpider
    data_type = 'release_package'

    def build_urls(self, project):
        id = project['id']
        for tag in ('planning', 'tender', 'award', 'contract'):
            url = f'{self.base_url}releases/{id}/{tag}'
            yield self.build_request(url.format(id=project['id'], tag=tag), formatter=components(-2))
