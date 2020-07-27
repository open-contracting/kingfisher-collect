import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class GeorgiaRecords(LinksSpider):
    """
    Swagger API documentation
      https://odapi.spa.ge/api/swagger.ui
    Spider arguments
      sample
        Downloads the first page of packages returned by the record list endpoint.
    """
    name = 'georgia_records'
    data_type = 'record_package'
    next_page_formatter = staticmethod(parameters('page'))
    skip_pluck = 'Already covered (see code for details)'  # georgia_releases

    def start_requests(self):
        url = 'https://odapi.spa.ge/api/records.json'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'})
