import scrapy

from kingfisher_scrapy.base_spiders import SimpleSpider
from kingfisher_scrapy.util import components, handle_http_error


class ItalyANAC(SimpleSpider):
    """
    Domain
      Autorità Nazionale Anticorruzione (ANAC)
    API documentation
      https://dati.anticorruzione.it/opendata/about
    Bulk download documentation
      https://dati.anticorruzione.it/opendata/organization/anticorruzione
    """
    name = 'italy_anac'
    download_timeout = 99999

    # SimpleSpider
    data_type = 'release_package'

    def start_requests(self):
        url = 'https://dati.anticorruzione.it/opendata/api/3/action/package_search?q=ocds'
        yield scrapy.Request(url, meta={'file_name': 'package_search.json'}, callback=self.parse_list)

    @handle_http_error
    def parse_list(self, response):
        data = response.json()
        for result in data['result']['results']:
            for resource in result['resources']:
                if resource['format'].upper() == 'JSON':
                    yield self.build_request(resource['url'], formatter=components(-2))
