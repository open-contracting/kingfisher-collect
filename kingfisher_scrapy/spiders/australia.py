from datetime import date

import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class Australia(LinksSpider):
    """
    Domain
      AusTender
    API documentation
      https://github.com/austender/austender-ocds-api
    Swagger API documentation
      https://app.swaggerhub.com/apis/austender/ocds-api/1.1
    """
    name = 'australia'
    data_type = 'release_package'
    next_page_formatter = staticmethod(parameters('cursor'))

    def start_requests(self):
        url = f'https://api.tenders.gov.au/ocds/findByDates/contractPublished/' \
              f'2004-01-01T00:00:00Z/{date.today().year}-12-31T23:59:59Z'
        yield scrapy.Request(url, meta={'file_name': 'start.json'})
