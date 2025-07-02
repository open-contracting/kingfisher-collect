import scrapy

from kingfisher_scrapy.base_spiders import CompressedFileSpider
from kingfisher_scrapy.util import MAX_DOWNLOAD_TIMEOUT


class GeorgiaOpendata(CompressedFileSpider):
    """
    Domain
      State Procurement Agency (SPA)
    """

    name = "georgia_opendata"
    # The file is about 450MB.
    download_timeout = MAX_DOWNLOAD_TIMEOUT

    # SimpleSpider
    data_type = "release_package"

    def start_requests(self):
        yield scrapy.Request("http://opendata.spa.ge/json/allTenders.zip", meta={"file_name": "all.zip"})
