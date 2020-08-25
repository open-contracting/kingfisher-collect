from kingfisher_scrapy.spiders.nigeria_budeshi_base import NigeriaBudeshiBase


class NigeriaBudeshiReleases(NigeriaBudeshiBase):
    """
    API documentation
      https://budeshi.ng/Api
    Spider arguments
      sample
        Download only the release package with project id = 1.
    """
    name = 'nigeria_budeshi_releases'
    data_type = 'release_package'
    url = 'https://budeshi.ng/api/releases/{}'
