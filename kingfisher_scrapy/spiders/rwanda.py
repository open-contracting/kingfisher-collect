import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class Rwanda(LinksSpider):
    """
    Domain
      Rwanda Public Procurement Authority (RPPA)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2016-07-02'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    Swagger API documentation
      https://ocds.umucyo.gov.rw/core/api/docs
    """
    name = 'rwanda'

    # BaseSpider
    default_from_date = '2016-07-02'
    date_required = True

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    formatter = staticmethod(parameters('PageNumber', 'dateFrom', 'dateTo'))

    def start_requests(self):
        from_date = self.from_date.strftime(self.date_format)
        until_date = self.until_date.strftime(self.date_format)
        url = (
            'https://ocds.umucyo.gov.rw/core/api/v1/releases/all'
            f'?PageNumber=1&PageSize=50&dateFrom={from_date}&dateTo={until_date} '
        )
        yield scrapy.Request(url, meta={'file_name': f'page-1-{from_date}.json'})
