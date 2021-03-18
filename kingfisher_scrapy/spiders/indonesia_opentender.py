from kingfisher_scrapy.base_spider import CompressedFileSpider, PeriodicSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters


class IndonesiaOpentender(CompressedFileSpider, PeriodicSpider):
    """
       Domain
         Open Tender
       Spider arguments
         from_date
           Download only releases from this date onward (YYYY format).
           If ``from_date`` is not provided defaults to 2008.
         until_date
           Download only releases until this date (YYYY format).
           If ``from_date`` is not provided defaults to current year.
       Bulk download documentation
         https://v3.opentender.net/#/ocds
    """

    name = 'indonesia_opentender'

    # BaseSpider
    date_format = 'year'
    default_from_date = '2008'

    # SimpleSpider
    data_type = 'release_package'

    base_url = 'https://opentender.net/api/'
    # PeriodicSpider
    pattern = base_url + 'master/lpse?year={}'
    start_requests_callback = 'parse_list'

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        year = response.request.url.split('=')[1]
        for item in data['data']:
            code = item['code']
            if code:
                url = f'{self.base_url}tender/export-ocds-batch?year={year}&lpse={code}'
                yield self.build_request(url, formatter=join(components(-1),
                                                             parameters('year', 'lpse'), extension='zip'))

    def get_formatter(self):
        return components(-1)
