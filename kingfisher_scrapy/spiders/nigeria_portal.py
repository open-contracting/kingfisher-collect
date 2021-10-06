from kingfisher_scrapy.spiders.nigeria_portal_base import NigeriaPortalBase


class NigeriaPortal(NigeriaPortalBase):
    """
    Domain
      Nigeria Open Contracting Portal (NOCOPO) of Bureau of Public Procurement (BPP)
    """
    name = 'nigeria_portal'
    download_delay = 0.9

    # SimpleSpider
    data_type = 'release_package'

    # NigeriaPortalBase
    base_url = 'http://nocopo.bpp.gov.ng/OpenData.aspx'
