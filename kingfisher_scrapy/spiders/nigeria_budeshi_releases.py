from kingfisher_scrapy.spiders.nigeria_budeshi_base import NigeriaBudeshiBase


class NigeriaBudeshiReleases(NigeriaBudeshiBase):
    """
    API documentation
      https://budeshi.ng/Api
    Spider arguments
      sample
       Sets the number of record packages to download.
    """
    name = 'nigeria_budeshi_releases'
    data_type = 'release_package'
    url = 'https://budeshi.ng/api/releases/{}'
