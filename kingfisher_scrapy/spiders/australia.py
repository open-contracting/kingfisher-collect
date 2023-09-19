import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class Australia(LinksSpider):
    """
    Domain
      AusTender
    Spider arguments
      from_date
        Download only data from this time onward (YYYY-MM-DDThh:mm:ss format). Defaults to '2004-01-01T00:00:00'.
      until_date
        Download only data until this time (YYYY-MM-DDThh:mm:ss format). Defaults to now.
    API documentation
      https://github.com/austender/austender-ocds-api
    Swagger API documentation
      https://app.swaggerhub.com/apis/austender/ocds-api/1.1
    """
    name = 'australia'

    # BaseSpider
    date_format = 'datetime'
    default_from_date = '2004-01-01T00:00:00'
    date_required = True

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    formatter = staticmethod(parameters('cursor'))

    def start_requests(self):
        from_date = self.from_date.strftime(self.date_format)
        until_date = self.until_date.strftime(self.date_format)
        url = f'https://api.tenders.gov.au/ocds/findByDates/contractPublished/{from_date}Z/{until_date}Z'

        yield scrapy.Request(url, meta={'file_name': f'{until_date}.json'})  # reverse chronological order
