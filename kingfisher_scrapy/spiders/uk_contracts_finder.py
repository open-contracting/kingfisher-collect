import json

from kingfisher_scrapy.base_spider import BaseSpider
from kingfisher_scrapy.util import components, handle_error, parameters, replace_parameter


class UKContractsFinder(BaseSpider):
    name = 'uk_contracts_finder'
    data_type = 'release_package_list_in_results'
    encoding = 'iso-8859-1'

    def start_requests(self):
        url = 'https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search?order=asc&page=1'
        yield self.build_request(url, formatter=parameters('page'), callback=self.parse_list)

    @handle_error
    def parse_list(self, response):
        yield from self.parse(response)

        if not self.sample:
            data = json.loads(response.text)
            total = data['maxPage']
            for page in range(2, total + 1):
                url = replace_parameter(response.request.url, 'page', page)
                yield self.build_request(url, formatter=components('page'))
