from kingfisher_scrapy.spiders.nigeria_budeshi_records import NigeriaBudeshiRecords


class NigeriaKadunaStateBudeshiRecords(NigeriaBudeshiRecords):
    """
    Domain
      Nigeria - Kaduna State
    API documentation
      https://kadppaocds.azurewebsites.net/api
    """
    name = 'nigeria_kaduna_state_budeshi_records'

    # NigeriaBudeshiBase
    base_url = 'https://kadppaocds.azurewebsites.net/api/'
