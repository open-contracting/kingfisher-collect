import json

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters, replace_parameter


class MoldovaMTender(SimpleSpider):
    """
    Spider arguments
      sample
        Download only one set of releases.
    """
    name = 'moldova_mtender'
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://public.mtender.gov.md/tenders/'
        yield self.build_request(url, formatter=components(-1), callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        base_url = 'http://public.eprocurement.systems/ocds/tenders/'
        data = json.loads(response.text)
        # The last page returns an empty JSON object.
        if not data:
            return
        for item in data['data']:
            yield self.build_request(base_url + item['ocid'], formatter=components(-1))

        if self.sample:
            return

        url = replace_parameter(response.request.url, 'offset', data['offset'])
        yield self.build_request(url, formatter=join(components(-1), parameters('offset')), callback=self.parse_list)
