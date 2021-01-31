import scrapy

from kingfisher_scrapy.base_spider import CompressedFileSpider


class GeorgiaOpenData(CompressedFileSpider):
    """
    Domain
      State Procurement Agency (SPA)
    """
    name = 'georgia_opendata'
    data_type = 'release_package'

    # The file is about 450MB.
    download_timeout = 1200  # 20min

    def start_requests(self):
        yield scrapy.Request('http://opendata.spa.ge/json/allTenders.zip', meta={'file_name': 'all.json'})
