import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.spiders.nigeria_bon_maximus_base import NigeriaBonMaximusBase
from kingfisher_scrapy.util import components, get_parameter_value, handle_http_error


class NigeriaOsunState(NigeriaBonMaximusBase):
    """
    Domain
      Nigeria Osun State Open Contracting Portal
    Bulk download documentation
      https://egp.osunstate.gov.ng/awarded_contracts.php
    """
    name = 'nigeria_osun_state'

    # SimpleSpider
    data_type = 'release_package'

    # NigeriaBonMaximusBase
    url_prefix = 'https://egp.osunstate.gov.ng/'
