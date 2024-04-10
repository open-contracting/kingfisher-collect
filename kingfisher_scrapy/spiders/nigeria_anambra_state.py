from kingfisher_scrapy.spiders.nigeria_bon_maximus_base import NigeriaBonMaximusBase


class NigeriaAnambraState(NigeriaBonMaximusBase):
    """
    Domain
      Anambra State
    API documentation
      https://eprocure.bpp.an.gov.ng/awarded_contracts.php
    """
    name = 'nigeria_anambra_state'

    # BaseSpider
    validate_json = True

    # SimpleSpider
    data_type = 'release_package'

    # NigeriaBonMaximusBase
    url_prefix = 'https://eprocure.bpp.an.gov.ng/'
