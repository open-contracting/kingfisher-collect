from kingfisher_scrapy.spiders.nigeria_kaduna_state_budeshi_base import NigeriaKadunaStateBudeshiBase
from kingfisher_scrapy.util import components


class NigeriaKadunaStateBudeshiReleases(NigeriaKadunaStateBudeshiBase):
    """
    Domain
        Budeshi Nigeria - Kaduna State
    API documentation
        https://www.budeshi.ng/kadppa/api
    """
    name = 'nigeria_kaduna_state_budeshi_releases'

    # SimpleSpider
    data_type = 'release_package'

    def build_urls(self, id):
        for tag in ('planning', 'tender', 'award', 'contract'):
            url = f'{self.base_url}releases/{id}/{tag}'
            yield self.build_request(url, formatter=components(-2))
