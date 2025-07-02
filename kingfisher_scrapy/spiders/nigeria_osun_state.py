from kingfisher_scrapy.spiders.nigeria_bon_maximus_base import NigeriaBonMaximusBase


class NigeriaOsunState(NigeriaBonMaximusBase):
    """
    Domain
      Osun State e-Procurement System
    Bulk download documentation
      https://egp.osunstate.gov.ng/awarded_contracts.php
    """

    name = "nigeria_osun_state"

    # BaseSpider
    validate_json = True  # https://github.com/open-contracting/kingfisher-collect/issues/963

    # SimpleSpider
    data_type = "release_package"

    # NigeriaBonMaximusBase
    url_prefix = "https://egp.osunstate.gov.ng/"
