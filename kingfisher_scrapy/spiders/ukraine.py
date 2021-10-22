import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import (append_path_components, components, handle_http_error, join, parameters,
                                    replace_parameters)


class Ukraine(SimpleSpider):
    """
    Domain
      ProZorro OpenProcurement API
    Caveats
      The API returns OCDS-like tenders and contracts objects, however an ocid is not set. Therefore, as part of this
      spider, the tender.id is used and added as the ocid.
    API documentation
      https://prozorro-api-docs.readthedocs.io/uk/latest/tendering/index.html
    """
    name = 'ukraine'
    base_url = 'https://public.api.openprocurement.org/api/0/'

    # BaseSpider
    encoding = 'utf-16'
    data_type = 'release'
    ocds_version = '1.0'

    def start_requests(self):
        for stage in ['tenders', 'contracts']:
            yield scrapy.Request(f'{self.base_url}{stage}', meta={'file_name': 'list.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = response.json()

        for item in data['data']:
            url = append_path_components(replace_parameters(response.request.url, offset=None), item['id'])
            yield self.build_request(url, formatter=components(-2))

        yield self.build_request(data['next_page']['uri'], formatter=join(components(-1), parameters('offset')),
                                 callback=self.parse_list)

    @handle_http_error
    def parse(self, response):
        data = response.json()
        if 'tenders' in response.request.url:
            # the Ukraine publication doesn't have an ocid, but the id field in the tender JSON can be used as one
            data['data']['ocid'] = data['data']['id']
            # the data looks like:
            # {
            #   "data": {
            #     "id": "..",
            #     "date": "...",
            #     "tenderID": "",
            #     tender fields
            #    }
            # }
            data = {'tender': data['data'], 'date': data['data']['date'], 'id': data['data']['id']}
        else:
            # the Ukraine publication doesn't have an ocid, but the tender_id field in the contract JSON
            # can be used as one, as it is the same as tender.id in the tender JSON and therefore can be used to link
            # both.
            data['data']['ocid'] = data['data']['tender_id']
            # the data looks like:
            # {
            #   "data": {
            #     "id": "",
            #     "contractID": "",
            #     contract fields
            #    }
            # }
            data = {'contracts': [data['data']], 'id': data['data']['id']}
        yield self.build_file_from_response(response, data=data, data_type=self.data_type)
