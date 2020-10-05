from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components


class NicaraguaSolidWaste(SimpleSpider):
    """
    Spider arguments
      sample
        Download only data released on 2013-01-23
      from_date
        Download only data from this date onward (YYYY-MM-DD format).
        If ``until_date`` is provided, defaults to '2000-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format).
        If ``from_date`` is provided, defaults to today.
    """
    name = 'nicaragua_solid_waste'
    data_type = 'release_package'
    default_from_date = '2000-01-01'
    url = 'http://www.gekoware.com/swmp/api/ocds/'

    def start_requests(self):
        if self.sample:
            # date parameter setting to get a one release from 2013
            url = self.url + '20130123/20130123'
        else:
            if self.from_date and self.until_date:
                # date parameter obtained
                url = self.url + self.from_date.strftime("%Y%m%d") + '/' + self.until_date.strftime("%Y%m%d")
            else:
                # date parameter setting to get all releases
                url = self.url + '20000101/20201231'

        # url looks like http://www.gekoware.com/swmp/api/ocds/20190101/20201005
        yield self.build_request(url, formatter=components(-2))
