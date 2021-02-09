from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error, join, parameters, replace_parameters


class Moldova(SimpleSpider):
    """
    Domain
      MTender
    """
    name = 'moldova'

    # SimpleSpider
    data_type = 'record_package'

    def start_requests(self):
        endpoints = {
            'budgets': 'https://public.mtender.gov.md/budgets/',
            # From https://github.com/open-contracting/kingfisher-collect/issues/192#issuecomment-529928683
            # The /tenders/plans endpoint appeared to return exactly the same data as the /tenders endpoint except
            # that when given an OCID parameter it returned an error message. It may be that /tenders/plans just
            # lists a subset of /tenders but this isn't clear.
            # 'plans': 'https://public.mtender.gov.md/tenders/plan/',
            'tenders': 'https://public.mtender.gov.md/tenders/',
        }

        for endpoint, url in endpoints.items():
            yield self.build_request(url, formatter=components(-1), callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        # The last page returns an empty JSON object.
        if not data:
            return

        for item in data['data']:
            url = replace_parameters(response.request.url, offset=None) + item['ocid']
            yield self.build_request(url, formatter=components(-2))

        url = replace_parameters(response.request.url, offset=data['offset'])
        yield self.build_request(url, formatter=join(components(-1), parameters('offset')), callback=self.parse_list)
