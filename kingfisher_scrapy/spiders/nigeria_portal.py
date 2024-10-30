import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider


class NigeriaPortal(CompressedFileSpider):
    """
    Domain
      Nigeria Open Contracting Portal (NOCOPO) - Bureau of Public Procurement (BPP)
    Bulk download documentation
        https://nocopo.bpp.gov.ng/Open-Data
    """

    name = 'nigeria_portal'
    download_timeout = 99999  # to avoid user timeout when downloading the file

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        # This follows a meta refresh.
        yield scrapy.Request('https://nocopo.bpp.gov.ng/ocdsjson.ashx?ocid=all', meta={'file_name': 'all.zip'})
