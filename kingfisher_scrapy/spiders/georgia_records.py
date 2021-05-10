import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class GeorgiaRecords(LinksSpider):
    """
    Domain
      State Procurement Agency (SPA)
    Bulk download documentation
      https://odapi.spa.ge/publication-policy
    """
    name = 'georgia_records'

    # BaseSpider
    skip_pluck = 'Already covered (see code for details)'  # georgia_releases

    # SimpleSpider
    data_type = 'record_package'

    # LinksSpider
    next_page_formatter = staticmethod(parameters('page'))

    def start_requests(self):
        url = 'https://odapi.spa.ge/api/records.json'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'})
