import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class DominicanRepublicAPI(LinksSpider):
    """
    Domain
      Dirección General de Contrataciones Públicas (DGCP)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2018-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    API documentation
      http://148.101.176.123:48080/ocdsdr/docs
    """
    name = 'dominican_republic_api'

    # BaseSpider
    default_from_date = '2018-01-01'

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    formatter = staticmethod(parameters('page'))

    def start_requests(self):
        url = 'http://148.101.176.123:48080/ocdsdr/api/v1/releases'
        if self.from_date and self.until_date:
            from_date = self.from_date.strftime(self.date_format)
            until_date = self.until_date.strftime(self.date_format)
            url = f'{url}/byDatesBetween/{from_date}/{until_date}'
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'})
