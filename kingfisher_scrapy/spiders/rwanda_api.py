import scrapy

from kingfisher_scrapy.base_spiders import LinksSpider
from kingfisher_scrapy.util import parameters


class RwandaAPI(LinksSpider):
    """
    Domain
      Rwanda Public Procurement Authority (RPPA)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2016-07-02'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    Swagger API documentation
      https://ocds.umucyo.gov.rw/opendata/api/docs
    """

    name = 'rwanda_api'

    # BaseSpider
    default_from_date = '2016-07-02'
    date_required = True

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    formatter = staticmethod(parameters('offset', 'date_from', 'date_to'))

    def start_requests(self):
        from_date = self.from_date.strftime(self.date_format)
        until_date = self.until_date.strftime(self.date_format)
        url = (
            'https://ocds.umucyo.gov.rw/opendata/api/v1/releases/all'
            f'?sort_field=date&sort_direction=desc&offset=0&limit=50&date_from={from_date}&date_to={until_date}'
        )
        yield scrapy.Request(url, meta={'file_name': f'page-1-{from_date}.json'})
