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

    # BaseSpider
    default_from_date = '2004-01-01T00:00:00'
    date_format = 'datetime'
    date_required = True

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    next_page_formatter = staticmethod(parameters('cursor'))

    def start_requests(self):
        url = f'https://api.tenders.gov.au/ocds/findByDates/contractPublished/' \
              f'{self.from_date.strftime(self.date_format)}Z/{self.until_date.strftime(self.date_format)}Z'

        yield scrapy.Request(url, meta={'file_name': 'start.json'})
