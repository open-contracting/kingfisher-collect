import json

from kingfisher_scrapy.base_spider import PeriodicSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters


class IndonesiaBandung(PeriodicSpider):
    """
    Domain
      Bandung Integrated Resource Management System (BIRMS)
    Spider arguments
      from_date
        Download only releases from this date onward (YYYY format).
        If ``from_date`` is not provided defaults to 2013.
      until_date
        Download only releases until this date (YYYY format).
        If ``from_date`` is not provided defaults to current year.
    API endpoints
      Get contract list by year
        Link
          ``https://birms.bandung.go.id/api/contracts/year/{year}?page={page}``
        Parameters
          year
            contract year number
          page
            page number
      Get contract detail by OCID
        Link
          ``https://birms.bandung.go.id/api/newcontract/ocds-afzrfb-{source-database}-{year}-{uniqid}``
        Parameters
          source-database
            (b)irms or (s)pse
          year
            contract year number
          uniqid
            release id
    """
    name = 'indonesia_bandung'
    data_type = 'release'

    # PeriodicSpider variables
    date_format = 'year'
    default_from_date = '2013'
    pattern = 'https://birms.bandung.go.id/api/packages/year/{}'
    start_requests_callback = 'parse_list'

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        for item in data['data']:
            url = item['uri']
            if url:
                yield self.build_request(url, self.get_formatter())
        else:
            next_page_url = data.get('next_page_url')
            if next_page_url:
                yield self.build_request(next_page_url, formatter=join(self.get_formatter(), parameters('page')),
                                         callback=self.parse_list)

    @handle_http_error
    def parse(self, response):
        data = response.json()
        if len(data) == 0:
            return
        yield self.build_file_from_response(response, data_type=self.data_type)

    def get_formatter(self):
        return components(-1)
