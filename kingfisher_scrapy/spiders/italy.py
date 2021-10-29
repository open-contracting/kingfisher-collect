import scrapy

from kingfisher_scrapy.base_spider import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class Italy(SimpleSpider):
    """
    Domain
      AppaltiPOP
    Bulk download documentation
      https://www.appaltipop.it/it/download
    """
    name = 'italy'

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        yield scrapy.Request(
            # From https://www.appaltipop.it/it/download
            'https://www.appaltipop.it/_next/data/LxpUO4Pg-S_nnq33fzaED/it/tenders.json',
            callback=self.parse_list
        )

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        # The data looks like:
        # {
        #   "pageProps": {
        #       other fields,
        #       "buyers": [ ... ],
        #       other fields
        #    },
        #   "__N_SSG": ...
        # }

        for buyer in data['pageProps']['buyers']:
            # The first resource in the list is the OCDS JSON, the second one a XLSX file
            resource = buyer['appaltipop:releases/0/buyer/dataSource/resources'][0]

            # The JSON file path looks like 'data/IT-CF-01232710374/ocds.json'
            filepath = resource['appaltipop:releases/0/buyer/resource/url']
            url = f'https://raw.githubusercontent.com/ondata/appaltipop/master/{filepath}'
            yield self.build_request(url, formatter=components(-2))
