import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class Colombia(LinksSpider):
    """
    Domain
      Colombia Compra Eficiente (CCE)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2011-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    API documentation
      https://www.colombiacompra.gov.co/transparencia/api
    Swagger API documentation
      https://apiocds.colombiacompra.gov.co/apiCCE2.0/
    """
    name = 'colombia'

    # BaseSpider
    default_from_date = '2011-01-01'
    # The endpoint without date parameters also works but is slower.
    date_required = True

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    next_page_formatter = staticmethod(parameters('_id'))

    def start_requests(self):
        url = 'https://apiocds.colombiacompra.gov.co/apiCCE2.0/rest/releases/dates/' \
              f'{self.from_date.strftime(self.date_format)}/{self.until_date.strftime(self.date_format)}'

        yield scrapy.Request(url, meta={'file_name': 'page-1.json'})
