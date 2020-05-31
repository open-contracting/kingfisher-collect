import scrapy

from kingfisher_scrapy.base_spider import LinksSpider


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

    def start_requests(self):
        yield scrapy.Request('https://odapi.spa.ge/api/records.json', meta={'kf_filename': 'page1.json'})
