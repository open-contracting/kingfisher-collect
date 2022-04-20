from kingfisher_scrapy.spiders.nigeria_budeshi_records import NigeriaBudeshiRecords
from kingfisher_scrapy.util import components


class NigeriaKadunaStateBudeshiRecords(NigeriaBudeshiRecords):
    """
    Domain
      Budeshi Nigeria - Kaduna State
    API documentation
      https://www.budeshi.ng/kadppa/api
    """
    name = 'nigeria_kaduna_state_budeshi_records'

    # NigeriaBudeshiBase
    base_url = 'https://www.budeshi.ng/kadppa/api/'
