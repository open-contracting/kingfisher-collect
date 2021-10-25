from kingfisher_scrapy.spiders.nigeria_portal_base import NigeriaPortalBase


class NigeriaGombeState(NigeriaPortalBase):
    """
    Domain
      Nigeria Gombe State Open Contracting Portal
    """
    name = 'nigeria_gombe_state'

    # SimpleSpider
    data_type = 'release_package'

    # NigeriaPortalBase
    base_url = 'http://gombe.stateopencontracting.com/Other-Basic/Report/Json-Report'
