from kingfisher_scrapy.base_spiders import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.util import components, get_parameter_value, handle_http_error, join, parameters


class IndonesiaOpentender(CompressedFileSpider, PeriodicSpider):
    """
    Domain
      Opentender.net
    Spider arguments
      from_date
        Download only data from this year onward (YYYY format). Defaults to '2008'.
      until_date
        Download only data until this year (YYYY format). Defaults to the current year.
    Bulk download documentation
      https://v3.opentender.net/#/ocds
    """

    name = 'indonesia_opentender'
    download_delay = 1 # to avoid the server producing incomplete JSON files.

    # Must be set before `pattern`, so we can't follow the standard order.
    url_prefix = 'https://opentender.net/api/'

    # BaseSpider
    date_format = 'year'
    default_from_date = '2008'

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = url_prefix + 'master/lpse?year={}&format=json'
    formatter = staticmethod(components(-1))
    start_requests_callback = 'parse_list'

    @handle_http_error
    def parse_list(self, response):
        year = get_parameter_value(response.request.url, 'year')
        codes_seen = set()
        for item in response.json()['data']:
            code = item['code']
            # There are duplicate codes.
            if code and code not in codes_seen:
                codes_seen.add(code)
                url = f'{self.url_prefix}tender/export-ocds-batch?year={year}&lpse={code}'
                yield self.build_request(
                    url,
                    formatter=join(components(-1), parameters('year', 'lpse'), extension='zip')
                )
