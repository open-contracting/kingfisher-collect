from kingfisher_scrapy.spiders.nigeria_budeshi_releases import NigeriaBudeshiReleases


class NigeriaKadunaStateBudeshiReleases(NigeriaBudeshiReleases):
    """
    Domain
      Nigeria - Kaduna State
    API documentation
      https://kadppaocds.azurewebsites.net/api
    """
    name = 'nigeria_kaduna_state_budeshi_releases'

    # NigeriaBudeshiBase
    base_url = 'https://kadppaocds.azurewebsites.net/api/'
