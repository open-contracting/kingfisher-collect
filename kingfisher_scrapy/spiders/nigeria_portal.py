import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider


class NigeriaPortal(CompressedFileSpider):
    """
    Domain
      Nigeria Open Contracting Portal (NOCOPO) of Bureau of Public Procurement (BPP)

    Bulk download documentation
        https://nocopo.bpp.gov.ng/Open-Data
    """
    name = 'nigeria_portal'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request('https://nocopo.bpp.gov.ng/ocdsjson.ashx?ocid=all', meta={'file_name': 'all.zip'})
