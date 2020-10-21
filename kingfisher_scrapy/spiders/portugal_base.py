import json
from io import BytesIO

import ijson
import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import get_parameter_value, handle_http_error, parameters, replace_parameters


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
        for number, data in enumerate(ijson.items(BytesIO(response.body), '', multiple_values=True, use_float=True)):
            if number == 10:
                break
            # get records service returns release packages
            if self.data_type == 'record_package':
                # the service returns one release per package
                ocid = data['releases'][0]['ocid']
                url = f'http://www.base.gov.pt/api/Record/GetRecordByOCID?ocid={ocid}'
                yield self.build_request(url, formatter=parameters('ocid'))
            else:
                json_array.append(data)
        if json_array:
            yield self.build_file_from_response(response, data=json.dumps(json_array), data_type=self.data_type)

        next_url = response.request.url
        offset = int(get_parameter_value(next_url, 'offset'))
        url = replace_parameters(next_url, offset=offset + 1)
        yield self.build_request(url, formatter=parameters('offset'), callback=self.parse_data)
