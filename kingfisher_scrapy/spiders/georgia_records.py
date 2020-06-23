import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class GeorgiaRecords(LinksSpider):
    """
    Swagger API documentation
      https://odapi.spa.ge/api/swagger.ui
    Spider arguments
      sample
        Download one set of releases.
    """
    name = 'georgia_records'
    data_type = 'record_package'
    next_page_formatter = staticmethod(parameters('page'))

    def start_requests(self):
        url = 'https://odapi.spa.ge/api/records.json'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'})
