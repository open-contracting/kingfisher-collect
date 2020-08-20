import scrapy
from urllib.parse import parse_qs, urlsplit

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import handle_http_error, parameters, replace_parameter


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
        yield from self.parse(response)

        if not self.sample:
            next_url = response.request.url
            query = parse_qs(urlsplit(next_url).query)
            offset = int(query['offset'][0])
            url = replace_parameter(next_url, 'offset', offset + 1)
            yield self.build_request(url, formatter=parameters('offset'), callback=self.parse_data)
