import json

import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class SpainZaragoza(SimpleSpider):
    """
    Swagger API documentation
      https://www.zaragoza.es/docs-api_sede/
    Spider arguments
      sample
        Downloads the first release returned by the API release endpoint.
      from_date
        Download only data from this date onward (YYYY-MM-DDTHH:mm:ss format).
        If ``until_date`` is provided, defaults to '2000-01-01T00:00:00'.
      until_date
        Download only data until this date (YYYY-MM-DDTHH:mm:ss format).
        If ``from_date`` is provided, defaults to today.
    """
    name = 'spain_zaragoza'
    data_type = 'release_list'
    date_format = 'datetime'
    default_from_date = '2000-01-01T00:00:00'
    url = 'https://www.zaragoza.es/sede/servicio/contratacion-publica/ocds/contracting-process/'

    def start_requests(self):
        # row parameter setting to 100000 to get all releases
        url = self.url + '?rf=html&rows=100000'

        # check date parameters and set "yyyy-MM-dd'T'HH:mm:ss'Z'" format
        if self.from_date and self.until_date:
            after = self.until_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            before = self.from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            url = url + '&before={}&after={}'.format(before, after)

        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        ids = json.loads(response.text)
        for contracting_process_id in ids:

            # A JSON array of ids strings
            url = self.url + contracting_process_id.get('id')
            yield self.build_request(url, formatter=components(-1))

            if self.sample:
                return
