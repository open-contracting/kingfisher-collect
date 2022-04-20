from kingfisher_scrapy.spiders.nigeria_budeshi_releases import NigeriaBudeshiReleases


class NigeriaKadunaStateBudeshiReleases(NigeriaBudeshiReleases):
    """
    Domain
      Budeshi Nigeria - Kaduna State
    API documentation
      https://www.budeshi.ng/kadppa/api
    """
    name = 'nigeria_kaduna_state_budeshi_releases'

    # NigeriaBudeshiBase
    base_url = 'https://www.budeshi.ng/kadppa/api/'
