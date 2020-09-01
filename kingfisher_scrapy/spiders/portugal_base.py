from io import BytesIO
from urllib.parse import parse_qs, urlsplit

import ijson
import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import get_parameter_value, handle_http_error, parameters, replace_parameter


class PortugalBase(SimpleSpider):
    default_from_date = '2010-01-01'
    download_delay = 1

    def start_requests(self):
        url = self.url
        if self.from_date and self.until_date:
            url = url + '&contractStartDate={}&contractEndDate={}'.format(self.from_date, self.until_date)
        yield scrapy.Request(url, meta={'file_name': 'offset-1.json'}, callback=self.parse_data)

    @handle_http_error
    def parse_data(self, response):
        json_array = []
        for data in ijson.items(BytesIO(response.body), '', multiple_values=True, use_float=True):
            json_array.append(data)
        yield self.build_file_from_response(response, data=json_array, data_type=self.data_type)

        if not self.sample:
            next_url = response.request.url
            offset = get_parameter_value(next_url, 'offset')
            url = replace_parameter(next_url, 'offset', offset + 1)
            yield self.build_request(url, formatter=parameters('offset'), callback=self.parse_data)
