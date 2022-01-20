import scrapy

from kingfisher_scrapy.base_spiders.compressed_file_spider import CompressedFileSpider


class GeorgiaOpendata(CompressedFileSpider):
    """
    Domain
      State Procurement Agency (SPA)
    """
    name = 'georgia_opendata'
    # The file is about 450MB.
    download_timeout = 1200  # 20min

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request('http://opendata.spa.ge/json/allTenders.zip', meta={'file_name': 'all.zip'})
