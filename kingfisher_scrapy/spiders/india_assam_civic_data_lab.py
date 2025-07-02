import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider


class IndiaAssamCivicDataLab(CompressedFileSpider):
    """
    Domain
      Assam State Government Finance Department
    Caveats
      The archived file contains a __MACOSX directory with a temporary ._package.json file that is omitted.
    Bulk download documentation
      https://github.com/CivicDataLab/assam-tenders-data/tree/main/data
    """

    name = "india_assam_civic_data_lab"

    # SimpleSpider
    data_type = "release_package"

    def start_requests(self):
        url = "https://github.com/CivicDataLab/assam-tenders-data/raw/main/data/ProcessedData/ocds-mapped-data/current/ocds_mapped_data.json.zip"
        yield scrapy.Request(url, meta={"file_name": "ocds_mapped_data.json.zip"})
