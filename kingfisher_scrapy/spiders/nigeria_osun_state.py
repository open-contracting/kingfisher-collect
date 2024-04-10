from kingfisher_scrapy.spiders.nigeria_bon_maximus_base import NigeriaBonMaximusBase


class NigeriaOsunState(NigeriaBonMaximusBase):
    """
    Domain
      Nigeria Osun State Open Contracting Portal
    Bulk download documentation
      https://egp.osunstate.gov.ng/awarded_contracts.php
    """
    name = 'nigeria_osun_state'

    # BaseSpider
    check_json_format = True

    # SimpleSpider
    data_type = 'release_package'

    # NigeriaBonMaximusBase
    url_prefix = 'https://egp.osunstate.gov.ng/'
