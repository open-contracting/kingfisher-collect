from kingfisher_scrapy.base_spider import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters


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

    base_url = 'https://opentender.net/api/'

    # BaseSpider
    date_format = 'year'
    default_from_date = '2008'

    # SimpleSpider
    data_type = 'release_package'

    # PeriodicSpider
    pattern = base_url + 'master/lpse?year={}'
    formatter = staticmethod(components(-1))
    start_requests_callback = 'parse_list'

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        year = response.request.url.split('=')[1]
        requested_codes = []
        for item in data['data']:
            code = item['code']
            # there are some duplicated codes
            if code and code not in requested_codes:
                requested_codes.append(code)
                url = f'{self.base_url}tender/export-ocds-batch?year={year}&lpse={code}'
                yield self.build_request(url, formatter=join(components(-1),
                                                             parameters('year', 'lpse'), extension='zip'))
