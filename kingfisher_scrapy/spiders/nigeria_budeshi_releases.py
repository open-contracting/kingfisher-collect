from kingfisher_scrapy.spiders.nigeria_budeshi_base import NigeriaBudeshiBase


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

    url = 'https://budeshi.ng/api/releases/{}'
