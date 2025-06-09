import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import MAX_DOWNLOAD_TIMEOUT


class NigeriaPortal(CompressedFileSpider):
    """
    Domain
      Nigeria Open Contracting Portal (NOCOPO) - Bureau of Public Procurement (BPP)
    Bulk download documentation
        https://nocopo.bpp.gov.ng/Open-Data
    """

    name = 'nigeria_portal'
    download_timeout = MAX_DOWNLOAD_TIMEOUT * 2  # 1h

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        # This follows a meta refresh.
        yield scrapy.Request('https://nocopo.bpp.gov.ng/ocdsjson.ashx?ocid=all', meta={'file_name': 'all.zip'})
