import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters, replace_parameters


class Moldova(SimpleSpider):
    """
    Domain
      MTender
    """
    name = 'moldova'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        # this URL list all the ocids and works with http://public.eprocurement.systems/ocds/tenders/ where the actual
        # valid OCDS data is returned (as one ocid per process)
        url = 'https://public.mtender.gov.md/tenders/'
        yield scrapy.Request(url, meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        base_url = 'http://public.eprocurement.systems/ocds/tenders/'
        data = response.json()
        # The last page returns an empty JSON object.
        if not data:
            return

        for item in data['data']:
            url = replace_parameters(base_url, offset=None) + item['ocid']
            yield self.build_request(url, formatter=components(-2))

        url = replace_parameters(response.request.url, offset=data['offset'])
        yield self.build_request(url, formatter=join(components(-1), parameters('offset')), callback=self.parse_list)
