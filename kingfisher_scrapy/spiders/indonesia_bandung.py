import json
from datetime import date

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import components, date_range_by_year, handle_http_error, join, parameters


class IndonesiaBandung(BaseSpider):
    """
    API endpoints
      Get Birms Contract List by year
        Link
          https://birms.bandung.go.id/api/contracts/year/{year}?page={page}
        Parameters
          year
            contract year number
          page
            page number
      Get Birms Detail Contract by OCID
        Link
          https://birms.bandung.go.id/api/newcontract/ocds-afzrfb-{b/s}-{year}-{uniqid}
        Parameters
          b/s
            (b)irms or (s)pse
          year
            contract year number
          uniqid
            release id
    """
    name = 'indonesia_bandung'

    def start_requests(self):
        pattern = 'https://birms.bandung.go.id/api/packages/year/{}'

        start = 2013
        stop = date.today().year

        for year in date_range_by_year(start, stop):
            yield self.build_request(pattern.format(year), formatter=components(-1), callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = json.loads(response.text)
        for item in data['data']:
            url = item['uri']
            if url:
                yield self.build_request(url, formatter=components(-1))
                if self.sample:
                    break
        else:
            next_page_url = data.get('next_page_url')
            if next_page_url:
                yield self.build_request(next_page_url, formatter=join(components(-1), parameters('page')),
                                         callback=self.parse_list)

    @handle_http_error
    def parse(self, response):
        data = json.loads(response.text)
        if len(data) == 0:
            return
        yield self.build_file_from_response(response, data_type='release')
