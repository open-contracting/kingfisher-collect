import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider


class PackistanPPRAReleases(SimpleSpider):
    """
    Domain
      Pakistan Public Procurement Regulatory Authority (PPRA)
    API documentation
      https://www.ppra.org.pk/api/
    """
    name = 'pakistan_ppra_releases'
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request('https://www.ppra.org.pk/api/index.php/api/release', meta={'file_name': 'releases.json'})
