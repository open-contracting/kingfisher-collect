from kingfisher_scrapy.base_spiders import LinksSpider, PeriodicSpider
from kingfisher_scrapy.util import components, handle_http_error


class DominicanRepublicAPI(LinksSpider, PeriodicSpider):
    """
    Domain
      Dirección General de Contrataciones Públicas (DGCP)
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2018'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    API documentation
      https://api.dgcp.gob.do/api/docs
    """
    name = 'dominican_republic_api'
    custom_settings = {
        # Reduce the number of concurrent requests to avoid multiple failures.
        'CONCURRENT_REQUESTS': 1,
    }

    # BaseSpider
    default_from_date = '2018'
    date_format = 'year'

    # SimpleSpider
    data_type = 'release_package'

    # LinksSpider
    formatter = staticmethod(components(-2))  # year
    next_pointer = '/pagination/next'

    # PeriodicSpider
    pattern = 'https://api.dgcp.gob.do/api/year/{}/1?limit=1000'

    @handle_http_error
    def parse(self, response):
        data = response.json()
        for item in data['data']:
            yield self.build_request(item['url'], formatter=components(-1), callback=super().parse)
        yield self.next_link(response)
