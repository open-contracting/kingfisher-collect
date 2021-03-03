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
      start_page
        The page number from which to start crawling.
    API documentation
      https://www.colombiacompra.gov.co/transparencia/api
    Swagger API documentation
      https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/
    """
    name = 'colombia'

    # BaseSpider
    default_from_date = '2011-01-01'

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    next_page_formatter = staticmethod(parameters('_id'))

    def start_requests(self):
        base_url = 'https://apiocds.colombiacompra.gov.co:8443/apiCCE2.0/rest/releases'
        if self.from_date and self.until_date:
            from_date = self.from_date.strftime(self.date_format)
            until_date = self.until_date.strftime(self.date_format)
            base_url += f'/dates/{from_date}/{until_date}'

        base_url += '?page={}'

        start_page = 1
        if hasattr(self, 'start_page'):
            start_page = int(self.start_page)
        yield self.build_request(base_url.format(start_page), formatter=parameters('page'))
