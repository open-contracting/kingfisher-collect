from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components


class NicaraguaSolidWaste(SimpleSpider):
    """
    Domain
      Solid Waste Mitigation Platform (SWMP)
    Spider arguments
      from_date
        Download only data from this date onward (YYYY-MM-DD format). Defaults to '2000-01-01'.
      until_date
        Download only data until this date (YYYY-MM-DD format). Defaults to today.
    """
    name = 'nicaragua_solid_waste'

    # BaseSpider
    default_from_date = '2000-01-01'
    date_required = True

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = f'http://www.gekoware.com/swmp/api/ocds/{self.from_date.strftime("%Y%m%d")}/' \
              f'{self.until_date.strftime("%Y%m%d")}'
        yield self.build_request(url, formatter=components(-2))
