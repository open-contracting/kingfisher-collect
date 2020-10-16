import scrapy

from kingfisher_scrapy.base_spider import LinksSpider
from kingfisher_scrapy.util import parameters


class DominicanRepublicPortal(LinksSpider):
    """
    API documentation
      http://148.101.176.123:48080/ocdsdr/docs
    Spider arguments
      sample
        Sets the number of release packages to download.
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2018-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    """
    name = 'dominican_republic_api'
    data_type = 'release_package'
    default_from_date = '2018-01-01'
    next_page_formatter = staticmethod(parameters('page'))

    def start_requests(self):
        url = 'http://148.101.176.123:48080/ocdsdr/api/v1/releases'
        if self.from_date and self.until_date:
            url = url + '/byDatesBetween/{}/{}'.format(
                self.from_date.strftime('%Y-%m-%d'),
                self.until_date.strftime('%Y-%m-%d')
            )
        yield scrapy.Request(url, meta={'file_name': 'page-1.json'})
